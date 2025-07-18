from dataclasses import dataclass

import shapely
from ortools.sat.python import cp_model

from ..graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from .solver import Solver

"""
wenn ein or im Name ist True das erste und False das zweite
sonnst aktiviert True den constrient
"""


@dataclass
class Parameter:
    intersection: bool = False
    degree: bool = False
    exclude_edges: bool = False


class OrTools_Tri(Solver):
    NAME = "OrTools_tri"

    def __init__(self, graph: Graph_Wrapper) -> None:
        super().__init__(graph)
        self.name = self.NAME

    def setup(self, parameter: Parameter):
        self.graph.add_all_possible_edges(default_for_active=False)
        self.triangle = self.add_time(self.graph.get_all_triangles)()
        self.vars = {}
        for tri in self.triangle:
            if not isinstance(tri, tuple) or len(tri) != 3:
                raise ValueError("Each triangle must be a tuple of length 3.")
            self.vars[tri] = self.model.NewBoolVar(
                f"edge_{tri}",
            )
        self.tris_as_point = {
            (node1, node2, node3): (
                self.graph.get_point_from_node(node1),
                self.graph.get_point_from_node(node2),
                self.graph.get_point_from_node(node3),
            )
            for node1, node2, node3 in self.triangle
        }

        self.edge_to_triangles = {}

        for triangle in self.triangle:
            node1, node2, node3 = triangle
            # Get all three edges of the triangle
            edges = [
                (min(node1, node2), max(node1, node2)),
                (min(node2, node3), max(node2, node3)),
                (min(node1, node3), max(node1, node3)),
            ]

            # Add this triangle to each edge's list
            for edge in edges:
                if edge not in self.edge_to_triangles:
                    self.edge_to_triangles[edge] = []
                self.edge_to_triangles[edge].append(triangle)

    def pre_solve(self, parameter: Parameter):
        self.add_time(self.setup)(parameter)
        if not self.triangle:
            raise ValueError("No triangles found in the graph.")
        if parameter.intersection:
            self.add_time(self.intersection_constraint)()
        if parameter.degree:
            self.add_time(self.degree_constraint)()
        if parameter.exclude_edges:
            self.add_time(self.exclude_edges_constraint)()

    @staticmethod
    def triangles_intersect(
        tri1: tuple[shapely.Point, shapely.Point, shapely.Point],
        tri2: tuple[shapely.Point, shapely.Point, shapely.Point],
    ) -> bool:
        tri1_poly = shapely.Polygon(tri1)
        if not tri1_poly.is_valid:
            tri1_poly = shapely.LineString(tri1)
        tri2_poly = shapely.Polygon(tri2)
        if not tri2_poly.is_valid:
            tri2_poly = shapely.LineString(tri2)
        assert isinstance(tri1_poly, shapely.Polygon) or isinstance(
            tri1_poly, shapely.LineString
        )
        assert isinstance(tri2_poly, shapely.Polygon) or isinstance(
            tri2_poly, shapely.LineString
        )
        return tri1_poly.intersects(tri2_poly) and not tri1_poly.touches(tri2_poly)

    def intersection_constraint(self):
        if not self.triangle:
            raise ValueError("No triangles found in the graph.")

        for (
            tri1,
            intersection,
        ) in self.add_time(self.graph.get_all_triangles_intersections_cpp)().items():
            for tri2 in intersection:
                self.model.add(
                    self.vars[tri1] + self.vars[tri2] <= 1,
                )

    def degree_constraint(self):
        hull = self.graph.get_hull_nodes()
        for node in self.graph.get_all_nodes():
            tris = self.graph.get_triangles_from_node(node)
            degree = self.graph.get_desired_degree_node(node)
            if node in hull:
                degree -= 1
            # Sum of all triangle variables containing this node must be <= degree
            summ = sum(self.vars[tri] for tri in tris)
            self.model.add(summ == degree)  # type: ignore[reportCallIssue]

    def exclude_edges_constraint(self):
        for edge in self.graph.exclude_edge_partition:
            for tri in self.get_triangles_from_edge(edge):
                self.model.add(self.vars[tri] == 0)

    def get_triangles_from_edge(self, edge: tuple[int, int]) -> list[int]:
        sorted_edge = tuple(sorted(edge))
        return self.edge_to_triangles.get(sorted_edge, [])

    def _actual_solver(self, parameter: dict) -> dict:
        if not isinstance(parameter, dict):
            raise TypeError("Parameter must be a dictionary.")
        args = parameter.get("args", None)
        assert args is not None, "Parameter 'args' must be provided in the dictionary."
        parameter_data: Parameter = Parameter(**(args))

        try:
            self.model = cp_model.CpModel()
            self.time_pre_solve(self.pre_solve)(parameter_data)
            # Solve the optimization model
            solver = cp_model.CpSolver()
            solver.parameters.max_time_in_seconds = self.get_remaining_time()
            status = self.time_solver(solver.Solve)(self.model)

            success = False
            # Check if solution was found
            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                success = True
                for tri, var in self.vars.items():
                    if solver.BooleanValue(var):
                        for i in range(3):
                            node1, node2 = tri[i], tri[(i + 1) % 3]
                            edge = (min(node1, node2), max(node1, node2))
                            self.graph.activate_edge(edge)

            if not success:
                self.timeout_error()
                self.logger.warning(f"{self.name} did not find an optimal solution.")
            return {
                "success": success,
            }
        except TimeoutError:
            self.logger.warning(f"{self.name} timed out.")
            return {
                "success": False,
            }

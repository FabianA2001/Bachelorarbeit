from dataclasses import dataclass

import shapely
from gurobipy import GRB, Model

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


class Gurobi_Tri(Solver):
    NAME = "gurobi_tri"

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
            self.vars[tri] = self.model.addVar(
                vtype=GRB.BINARY,
                name=f"tri_{tri[0]}_{tri[1]}_{tri[2]}",
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
        all_edges = self.graph.get_all_edges()
        hull_nodes = self.graph.get_hull_nodes_sorted()
        for node1, node2 in zip(hull_nodes, hull_nodes[1:] + [hull_nodes[0]]):
            hull_edge = (node1, node2)
            # self.logger.info(f"Adding hull edge constraint for {hull_edge}")
            summ_hull = 0
            sorted_hull_edge = (min(hull_edge), max(hull_edge))
            if sorted_hull_edge in all_edges:
                all_edges.remove(sorted_hull_edge)
            for tri in self.graph.get_triangles_for_edge(hull_edge, check_active=False):
                # self.logger.info(f"Adding hull triangle {tri} for edge {hull_edge}")
                if tri[3] == -1:
                    if tri[:3] in self.vars:
                        summ_hull += self.vars[tri[:3]]
            assert not isinstance(summ_hull, int), "No triangles found for hull edge."
            self.model.addConstr(summ_hull == 1)

        left_summ = 0
        right_summ = 0
        for edge in all_edges:
            left_summ = 0
            right_summ = 0
            for tri in self.graph.get_triangles_for_edge(edge, check_active=False):
                if tri[3] == 1:
                    if tri[:3] in self.vars:
                        left_summ += self.vars[tri[:3]]
                else:
                    if tri[:3] in self.vars:
                        right_summ += self.vars[tri[:3]]
            assert not isinstance(left_summ, int) and not isinstance(right_summ, int), (
                "No triangles found for edge."
            )
            self.model.addConstr(left_summ == right_summ)

    def intersection_constraint_old(self):
        if not self.triangle:
            raise ValueError("No triangles found in the graph.")

        for (
            tri1,
            intersection,
        ) in self.add_time(self.graph.get_all_triangles_intersections_cpp)().items():
            for tri2 in intersection:
                self.model.addConstr(
                    self.vars[tri1] + self.vars[tri2] <= 1,
                    name=f"intersection_{tri1}_{tri2}",
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
            self.model.addConstr(summ == degree)  # type: ignore[reportCallIssue]

    def exclude_edges_constraint(self):
        for edge in self.graph.exclude_edges:
            for tri in self.get_triangles_from_edge(edge):
                self.model.addConstr(self.vars[tri] == 0)

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
            self.model = Model()
            self.time_pre_solve(self.pre_solve)(parameter_data)
            self.model.setParam("OutputFlag", 0)  # Suppress Gurobi output
            print(self.get_remaining_time())
            self.model.setParam("TimeLimit", self.get_remaining_time())  # Set timeout

            # Solve the optimization model
            self.time_solver(self.model.optimize)()

            success = False
            # Check if solution was found
            if self.model.status == GRB.OPTIMAL:
                success = True
                for tri, var in self.vars.items():
                    if var.X > 0.5:  # Variable is active (binary variable close to 1)
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

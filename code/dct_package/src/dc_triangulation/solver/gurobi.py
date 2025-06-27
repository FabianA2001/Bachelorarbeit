from dataclasses import dataclass

import shapely
from gurobipy import GRB, Model

from ..graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from ..utils import time_function
from .solver import Solver

"""
wenn ein or im Name ist True das erste und False das zweite
sonnst aktiviert True den constrient
"""


@dataclass
class Parameter:
    intersection: bool = False
    degree: bool = False


class Gurobi(Solver):
    NAME = "gurobi"

    def __init__(self, graph: Graph_Wrapper) -> None:
        super().__init__(graph)
        self.name = self.NAME

    def setup(self, parameter: Parameter):
        self.graph.add_all_possible_edges(default_for_active=False)
        self.triangle = time_function(self.graph.get_all_triangles, self.logger)()
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

    def pre_solve(self, parameter: Parameter):
        self.setup(parameter)
        if not self.triangle:
            raise ValueError("No triangles found in the graph.")
        if parameter.intersection:
            time_function(self.intersection_constraint, self.logger)()
        if parameter.degree:
            time_function(self.degree_constraint, self.logger)()

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
        ) in time_function(
            self.graph.get_all_triangles_intersections_cpp, self.logger
        )().items():
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

    def _actual_solver(self, parameter: dict) -> dict:
        if not isinstance(parameter, dict):
            raise TypeError("Parameter must be a dictionary.")
        args = parameter.get("args", None)
        assert args is not None, "Parameter 'args' must be provided in the dictionary."
        parameter_data: Parameter = Parameter(**(args))

        try:
            self.model = Model()
            self.model.setParam("OutputFlag", 0)  # Suppress Gurobi output
            self.time_pre_solve(self.pre_solve)(parameter_data)

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
                self.logger.warning(f"{self.name} did not find an optimal solution.")
            return {
                "success": success,
            }
        except TimeoutError:
            self.logger.warning(f"{self.name} timed out.")
            return {
                "success": False,
            }

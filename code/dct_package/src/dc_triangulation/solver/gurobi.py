from dataclasses import dataclass

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
    fix_hull: bool = False
    all_edges: bool = False


class Gurobi(Solver):
    NAME = "gurobi"

    def __init__(self, graph: Graph_Wrapper) -> None:
        super().__init__(graph)
        self.name = self.NAME

    def setup(self, parameter: Parameter):
        self.graph.add_all_possible_edges(default_for_active=False)
        self.vars = {}
        for edge in self.graph.get_all_edges():
            self.vars[edge] = self.model.addVar(
                vtype=GRB.BINARY,
                name=f"edge:({edge[0]},{edge[1]})",
            )

    def pre_solve(self, parameter: Parameter):
        self.add_time(self.setup)(parameter)
        if parameter.intersection:
            self.add_time(self.intersection_constraint)()
        if parameter.degree:
            self.add_time(self.degree_constraint)()
        if parameter.exclude_edges:
            self.add_time(self.exclude_edges_constraint)()
        if parameter.fix_hull:
            self.add_time(self.fix_hull_constraint)()
        if parameter.all_edges:
            self.add_time(self.all_edges_constraint)()
        self.timeout_error()

    def intersection_constraint(self):
        intersection_all = self.graph.get_all_intersections_cpp(self.timeout_error)
        for edge, intersections in intersection_all.items():
            for intersection in intersections:
                self.model.addConstr(self.vars[edge] + self.vars[intersection] <= 1)
        self.timeout_error()

    def degree_constraint(self):
        if self.graph is None:
            raise ValueError("Graph is not set. Please set the graph before solving.")
        for node in self.graph.get_all_nodes():
            degree = self.graph.get_desired_degree_node(node)
            summ = 0
            for edge in self.graph.get_edges_of_node(node):
                summ += self.vars[edge]
            self.model.addConstr(summ == degree)  # type: ignore[reportCallIssue]

    def exclude_edges_constraint(self):
        for edge in self.graph.exclude_edge_partition:
            self.model.addConstr(self.vars[edge] == 0)

    def all_edges_constraint(self):
        intersection_all = self.graph.get_all_intersections_cpp(self.timeout_error)
        for edge, intersections in intersection_all.items():
            self.model.addConstr(
                sum(self.vars[intersection] for intersection in intersections)
                + self.vars[edge]
                >= 1
            )

    def fix_hull_constraint(self):
        for edge in self.graph.get_hull_edges():
            self.model.addConstr(self.vars[edge] == 1)

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
            self.model.setParam("TimeLimit", self.get_remaining_time())  # Set timeout

            # Solve the optimization model
            self.time_solver(self.model.optimize)()

            success = False
            # Check if solution was found
            if self.model.status == GRB.OPTIMAL:
                success = True
                for edge, var in self.vars.items():
                    if var.X > 0.5:  # Variable is active (binary variable close to 1)
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

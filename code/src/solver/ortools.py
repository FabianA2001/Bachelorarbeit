from solver.solver import Solver
from ortools.sat.python import cp_model
from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
import logging


class FirstSolutionStop(cp_model.CpSolverSolutionCallback):
    def __init__(self, goal: int) -> None:
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.goal = goal
        self.version = "0.1"

    def on_solution_callback(self):
        if self.ObjectiveValue() >= self.goal:
            self.StopSearch()  # Stop after the first solution
        # logging.info(
        #     f"Anzahl Kanten bei dieser Lösung: {self.ObjectiveValue()}")


class Ortools(Solver):
    NAME = "Ortools"

    def __init__(self, graph: Graph_Wrapper) -> None:
        super().__init__(graph)
        self.name = self.NAME
        self.model = cp_model.CpModel()

    def constraint_intersection(self):
        if self.graph is None:
            raise ValueError("Graph is not set. Please set the graph before solving.")
        for edge, other_edge in self.graph.get_all_intersections(check_if_active=False):
            self.model.AddBoolOr([self.vars[edge].Not(), self.vars[other_edge].Not()])

    def constraint_degree(self):
        if self.graph is None:
            raise ValueError("Graph is not set. Please set the graph before solving.")
        for node in self.graph.get_all_nodes_name():
            degree = self.graph._data.nodes[node]["degree"]
            summ = 0
            for edge in self.graph._data.edges(node):
                if edge in self.vars:
                    summ += self.vars[edge]
                else:
                    summ += self.vars[(edge[1], edge[0])]
            self.model.Add(summ == degree)

    def constraint_number_edges(self, number_edges: int):
        if self.graph is None:
            raise ValueError("Graph is not set. Please set the graph before solving.")
        if number_edges < 0:
            raise ValueError("Number of edges must be non-negative.")
        summ = sum(self.vars.values())
        self.model.Add(summ == number_edges)

    def _actual_solver(self, parameter: dict) -> dict:
        if self.graph is None:
            raise ValueError("Graph is not set. Please set the graph before solving.")
        self.graph.add_all_possible_edges(default_for_active=False)
        self.vars = {
            edge: self.model.NewBoolVar(f"edge_{edge[0]}_{edge[1]}")
            for edge in self.graph.get_all_edges()
        }

        if parameter["version"] == 0.1:
            self.model.Maximize(sum(list(self.vars.values())))
            self.constraint_intersection()
            self.constraint_degree()
        elif parameter["version"] == 0.2:
            self.constraint_intersection()
            self.constraint_degree()
            self.constraint_number_edges(self.graph.get_number_edges_in_Triangulation())
        else:
            raise ValueError(
                f"Version {parameter['version']} for OrTools not supported."
            )

        solver = cp_model.CpSolver()
        # solver.parameters.log_search_progress = True  # Enable logging
        solver.parameters.max_time_in_seconds = self.get_remaining_time()
        logging.info("Start solving...")
        status = solver.Solve(
            self.model,
            FirstSolutionStop(self.graph.get_number_edges_in_Triangulation()),
        )
        # status = solver.Solve(self.model)
        if not (status == cp_model.OPTIMAL or status == cp_model.FEASIBLE):
            logging.warning("No solution found.")
            return {
                "success": False,
            }
        for edge, var in zip(self.graph.get_all_edges(), self.vars.values()):
            if solver.BooleanValue(var):
                self.graph.activate_edge(edge)
        return {
            "success": True,
        }

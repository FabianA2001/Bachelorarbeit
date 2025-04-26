from solver.solver import Solver
from ortools.sat.python import cp_model
from graph_utils.graph_wrapper import Graph_Wrapper
import logging
import itertools
from typing import Optional


class FirstSolutionStop(cp_model.CpSolverSolutionCallback):
    def __init__(self, goal: int) -> None:
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.goal = goal

    def on_solution_callback(self):
        if self.ObjectiveValue() >= self.goal:
            self.StopSearch()  # Stop after the first solution
        # logging.info(
        #     f"Anzahl Kanten bei dieser Lösung: {self.ObjectiveValue()}")


class Ortools(Solver):
    def __init__(self, graph: Optional[Graph_Wrapper] = None) -> None:
        super().__init__(graph)
        self.name = "Ortools"
        self.model = cp_model.CpModel()

    def constraint_intersection(self):
        if self.graph is None:
            raise ValueError("Graph is not set. Please set the graph before solving.")
        all_edges = self.graph.get_all_edges()
        combinations = list(itertools.combinations(all_edges, 2))
        for edge_1, edge_2 in combinations:
            if self.graph.check_for_intersection_except_corners(edge_1, edge_2):
                self.model.AddBoolOr([self.vars[edge_1].Not(), self.vars[edge_2].Not()])

    def constraint_degree(self):
        if self.graph is None:
            raise ValueError("Graph is not set. Please set the graph before solving.")
        for node in self.graph.get_all_nodes_name():
            degree = self.graph.nodes[node]["degree"]
            summ = 0
            for edge in self.graph.edges(node):
                if edge in self.vars:
                    summ += self.vars[edge]
                else:
                    summ += self.vars[(edge[1], edge[0])]
            self.model.Add(summ == degree)

    def _actual_solver(self):
        if self.graph is None:
            raise ValueError("Graph is not set. Please set the graph before solving.")
        self.graph.add_all_possible_edges()
        self.vars = {
            edge: self.model.NewBoolVar(f"edge_{edge[0]}_{edge[1]}")
            for edge in self.graph.get_all_edges()
        }
        self.model.Maximize(sum(list(self.vars.values())))
        self.constraint_intersection()
        self.constraint_degree()

        solver = cp_model.CpSolver()
        # solver.parameters.log_search_progress = True  # Enable logging
        logging.info("Start solving...")
        status = solver.Solve(
            self.model, FirstSolutionStop(self.graph.number_edges_in_Triangulation)
        )
        # status = solver.Solve(self.model)
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            for edge, var in zip(self.graph.get_all_edges(), self.vars.values()):
                if solver.BooleanValue(var):
                    self.graph.active_edge(edge)
        else:
            logging.error("No solution found.")

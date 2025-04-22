from solver.solver import Solver
from ortools.sat.python import cp_model
from graphe_utils.graphe import Graphe
import logging
import itertools


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
    def __init__(self, graphe: Graphe) -> None:
        super().__init__(graphe)
        self.name = "Ortools"
        self.graph.add_all_possible_edges()
        self.model = cp_model.CpModel()
        self.vars = {
            edge: self.model.NewBoolVar(f"edge_{edge[0]}_{edge[1]}")
            for edge in self.graph.get_all_edges()
        }
        self.model.Maximize(sum(list(self.vars.values())))
        self.constraint_intersection()
        self.constraint_degree()

    def constraint_intersection(self):
        all_edges = self.graph.get_all_edges()
        combinations = list(itertools.combinations(all_edges, 2))
        for edge_1, edge_2 in combinations:
            if self.graph.check_for_intersection_ececpt_corners(edge_1, edge_2):
                self.model.AddBoolOr(
                    [self.vars[edge_1].Not(), self.vars[edge_2].Not()])

    def constraint_degree(self):
        for node in self.graph.get_all_nodes_name():
            degree = self.graph.graph.nodes[node]["degree"]
            summ = 0
            for edge in self.graph.graph.edges(node):
                if edge in self.vars:
                    summ += self.vars[edge]
                else:
                    summ += self.vars[(edge[1], edge[0])]
            self.model.Add(summ == degree)

    def _actual_solver(self):
        solver = cp_model.CpSolver()
        # solver.parameters.log_search_progress = True  # Enable logging
        logging.info("Start solving...")
        status = solver.Solve(
            self.model, FirstSolutionStop(
                self.graph.number_edges_in_Triangulatoin)
        )
        # status = solver.Solve(self.model)
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            for edge, var in zip(self.graph.get_all_edges(), self.vars.values()):
                if solver.BooleanValue(var):
                    self.graph.active_edge(edge)
        else:
            logging.error("No solution found.")

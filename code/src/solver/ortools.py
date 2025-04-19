from solver.solver import Solver
from ortools.sat.python import cp_model
from graphe_utils.graphe import Graphe
import logging
import itertools


class FirstSolutionStop(cp_model.CpSolverSolutionCallback):
    def __init__(self):
        cp_model.CpSolverSolutionCallback.__init__(self)

    def on_solution_callback(self):
        # self.StopSearch()  # Stop after the first solution
        logging.info(f"Anzahl Kanten bei dieser Lösung: {self.ObjectiveValue()}")


class Ortools(Solver):
    def __init__(self, graphe: Graphe) -> None:
        logging.info("Ortools solver erstellt.")
        super().__init__(graphe)
        self.graph.add_all_possible_edges()
        self.model = cp_model.CpModel()
        self.vars = [
            self.model.NewBoolVar(f"edge_{edge[0]}_{edge[1]}")
            for edge in self.graph.get_all_edges()
        ]

        self.model.Maximize(sum(self.vars))
        self.constraint_intersection()

    def constraint_intersection(self):
        combinations = list(itertools.combinations(range(len(self.vars)), 2))
        all_edges = self.graph.get_all_edges()
        for index_1, index_2 in combinations:
            if self.graph.check_for_intersection_ececpt_corners(
                all_edges[index_1], all_edges[index_2]
            ):
                self.model.AddBoolOr(
                    [self.vars[index_1].Not(), self.vars[index_2].Not()]
                )

    def actual_solver(self):
        solver = cp_model.CpSolver()
        # solver.parameters.log_search_progress = True  # Enable logging
        logging.info("Start solving...")
        status = solver.Solve(self.model, FirstSolutionStop())
        # status = solver.Solve(self.model)
        logging.info(f"Status: {solver.StatusName(status)}")
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            for edge, var in zip(self.graph.get_all_edges(), self.vars):
                if solver.BooleanValue(var):
                    self.graph.active_edge(edge)
        else:
            logging.error("No solution found.")

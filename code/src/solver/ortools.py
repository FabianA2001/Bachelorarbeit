from solver.solver import Solver
from ortools.sat.python import cp_model
from graphe_utils.graphe import Graphe
import logging


class Ortools(Solver):
    def __init__(self, graphe: Graphe) -> None:
        logging.info("Ortools solver erstellt.")
        super().__init__(graphe)
        self.model = cp_model.CpModel()
        self.vars = [
            self.model.NewBoolVar(f"edge_{edge[0]}_{edge[1]}")
            for edge in self.graph.get_all_edges()
        ]

        self.model.Maximize(sum(self.vars))

    def actual_solver(self):
        solver = cp_model.CpSolver()
        status = solver.Solve(self.model)
        logging.info(f"Status: {solver.StatusName(status)}")
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            for edge, var in zip(self.graph.get_all_edges(), self.vars):
                if solver.BooleanValue(var):
                    self.graph.active_edge(edge[0], edge[1])
        else:
            logging.error("No solution found.")

from dataclasses import asdict

from ..graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from .sat import SAT
from .sat import Parameter as SAT_Parameter
from .solver import Solver


class Count(Solver):
    NAME = "Count"

    def __init__(self, graph: Graph_Wrapper, max_try: int = 1000) -> None:
        super().__init__(graph)
        self.logger.warning("gibt zusätzlich anzahl zurück")
        self.name = self.NAME
        self.max_try = max_try

    def _actual_solver(self, parameter: dict) -> dict:
        if self.graph is None:
            raise ValueError("Graph is not set. Please set the graph before solving.")

        assert self.graph.get_all_edges() == [], (
            "Graph is not empty. Please clear the graph before solving."
        )
        counter = 0
        seen_clauses = []
        para = asdict(
            SAT_Parameter(
                intersection=True, degree_atleast=True, all_edges=True, fix_hull=True
            )
        )
        solver = SAT(self.graph)
        for _ in range(self.max_try):
            result = solver.solve(
                {
                    "timeout": self.get_remaining_time(),
                    "args": para,
                    "debug_clauses": seen_clauses,
                }
            )
            if result["success"]:
                counter += 1

                seen_clauses.append([])
            else:
                self.logger.info("No more solutions found.")
                break

        return {
            "success": True,
            "count": counter,
        }

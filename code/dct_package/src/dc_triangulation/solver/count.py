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
        self.logger.warning("kein Timeout")
        self.name = self.NAME
        self.max_try = max_try

    def _actual_solver(self, parameter: dict) -> dict:
        if self.graph is None:
            raise ValueError("Graph is not set. Please set the graph before solving.")

        assert self.graph.get_all_edges() == [], (
            "Graph is not empty. Please clear the graph before solving."
        )
        para = asdict(
            SAT_Parameter(
                solver_name="Gluecard4",
                degree_encoding=9,
                intersection=True,
                degree_atleast=True,
                fix_hull=True,
            )
        )
        solver = SAT(self.graph)
        result = solver.solve(
            {
                "timeout": self.get_remaining_time(),
                "args": para,
            }
        )
        counter = 1
        seen_combinations = [self.graph.get_all_active_edges()]
        try:
            for _ in range(self.max_try):
                self.graph.deactivate_all_edges()
                result = solver.second_run(
                    {
                        "timeout": self.get_remaining_time(),
                        "args": para,
                        "seen_combinations": seen_combinations,
                    },
                )
                seen_combinations.append(self.graph.get_all_active_edges())
                if result["success"]:
                    counter += 1
                elif not result.get("timeout", True):
                    self.logger.info("No more solutions found.")
                    break
                else:
                    raise TimeoutError(
                        "Timeout reached during counting. Consider increasing the max_try limit."
                    )

            return {
                "success": True,
                "count": counter,
                "seen_combinations": seen_combinations,
            }
        except TimeoutError as e:
            self.logger.warning(f"{self.name} timed out: {e}")
            return {
                "success": False,
                "timeout": True,
                "count": counter,
                "seen_combinations": seen_combinations,
            }

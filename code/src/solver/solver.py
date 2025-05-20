from abc import ABC, abstractmethod
from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
import logging
from typing import Optional


class Solver(ABC):
    """
    Abstract base class for all solvers.
    """

    def __init__(self, graph: Optional[Graph_Wrapper] = None) -> None:
        self.name = "Solver"
        self.graph: Optional[Graph_Wrapper] = graph

    def solve(self, timeout: int = -1) -> bool:
        if not isinstance(self.graph, Graph_Wrapper):
            raise ValueError("Graph is not set. Please set the graph before solving.")
        logging.info(f"{self.name} started.")
        self.graph.name = self.name
        result = self._actual_solver()
        logging.info(f"{self.name} completed.")
        return result

    @abstractmethod
    def _actual_solver(self) -> bool: ...

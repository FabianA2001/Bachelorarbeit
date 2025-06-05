from abc import ABC, abstractmethod
from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
import logging


class Solution:
    def __init__(self, success: bool) -> None:
        self.success = success


class Solver(ABC):
    """
    Abstract base class for all solvers.
    """

    VERSION = "0.1"
    NAME = "Solver"

    def __init__(self, graph: Graph_Wrapper) -> None:
        self.name = self.NAME
        self.graph: Graph_Wrapper = graph
        self.success = False

    def __str__(self) -> str:
        return self.name

    def solve(self, timeout: int = -1) -> Solution:
        if not isinstance(self.graph, Graph_Wrapper):
            raise ValueError("Graph is not set. Please set the graph before solving.")
        logging.info(f"{self.name} started.")
        self.graph.name = self.name

        solution = self._actual_solver()
        logging.info(f"{self.name} completed.")
        return solution

    @abstractmethod
    def _actual_solver(self) -> Solution: ...

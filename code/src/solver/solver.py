from abc import ABC, abstractmethod
from graphe_utils.graph_wrapper import Graph_Wrapper
import logging


class Solver(ABC):
    """
    Abstract base class for all solvers.
    """

    def __init__(self, graph: Graph_Wrapper) -> None:
        self.name = "Solver"
        self.graph: Graph_Wrapper = graph

    def solve(self) -> Graph_Wrapper:
        logging.info(f"{self.name} started.")
        self.graph.graph_name = self.name
        self._actual_solver()
        logging.info(f"{self.name} completed.")
        return self.graph

    @abstractmethod
    def _actual_solver(self): ...

from abc import ABC, abstractmethod
from graphe_utils.graphe import Graphe
import logging


class Solver(ABC):
    """
    Abstract base class for all solvers.
    """

    def __init__(self, graph: Graphe) -> None:
        self.name = "Solver"
        self.graph: Graphe = graph

    def solve(self) -> Graphe:
        logging.info(f"{self.name} started.")
        self.graph.name = self.name
        self.actual_solver()
        logging.info(f"{self.name} completed.")
        return self.graph

    @abstractmethod
    def actual_solver(self): ...

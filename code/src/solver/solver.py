from abc import ABC, abstractmethod
from graphe_utils.graphe import Graphe


class Solver(ABC):
    """
    Abstract base class for all solvers.
    """

    def solve(self, graphe: Graphe) -> Graphe:
        self.graph: Graphe = graphe
        self.actual_solver()
        return self.graph

    @abstractmethod
    def actual_solver(self): ...

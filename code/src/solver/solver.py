from abc import ABC, abstractmethod
from graphe_utils.graphe import Graphe


class Solver(ABC):
    """
    Abstract base class for all solvers.
    """

    def __init__(self, graphe: Graphe) -> None:
        self.graph: Graphe = graphe

    def solve(self) -> Graphe:
        self.actual_solver()
        return self.graph

    @abstractmethod
    def actual_solver(self): ...

from abc import ABC, abstractmethod
from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
import logging
import time


class TimeoutError(Exception):
    """Custom exception for timeout errors."""

    pass


class Solver(ABC):
    """
    Abstract base class for all solvers.
    """

    NAME = "Solver"

    def __init__(self, graph: Graph_Wrapper) -> None:
        self.name = self.NAME
        self.graph: Graph_Wrapper = graph
        self.success = False
        self.start_time = None
        self.timeout = -1  # Default timeout value, can be overridden

    def __str__(self) -> str:
        return self.name

    def get_remaining_time(self) -> float:
        if self.start_time is None:
            raise ValueError("Solver has not started yet.")
        return (
            self.timeout - (time.time() - self.start_time)
            if self.timeout > 0
            else float("inf")
        )

    def reach_timeout(self) -> bool:
        if self.timeout < 0:
            return False
        if self.start_time is None:
            raise ValueError("Solver has not started yet.")
        elapsed_time = time.time() - self.start_time
        if elapsed_time > self.timeout:
            logging.warning(f"{self.name} timed out after {elapsed_time:.2f} seconds.")
            return True
        return False

    def timeout_error(self):
        if self.reach_timeout():
            raise TimeoutError()

    def solve(self, parameter: dict) -> dict:
        if not isinstance(self.graph, Graph_Wrapper):
            raise ValueError("Graph is not set. Please set the graph before solving.")
        logging.info(f"{self.name} started.")
        self.timeout = parameter["timeout"]
        self.start_time = time.time()
        self.graph.name = self.name

        solution = self._actual_solver(parameter)
        logging.info(f"{self.name} completed.")
        return solution

    @abstractmethod
    def _actual_solver(self, parameter: dict) -> dict: ...

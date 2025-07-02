import logging
import time
from abc import ABC, abstractmethod

from ..graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from ..utils import format_dictionary


class TimeoutError(Exception):
    """Custom exception for timeout errors."""

    pass


class Solver(ABC):
    """
    Abstract base class for all solvers.
    """

    NAME = "Solver"
    LOGGER_NAME = "solver_logger"

    def __init__(self, graph: Graph_Wrapper) -> None:
        self.name = self.NAME
        self.graph: Graph_Wrapper = graph
        self.success = False
        self.start_time = None
        self.timeout = -1  # Default timeout value, can be overridden
        self.solve_time = -1.0
        self.pre_solve_time = -1.0
        self.logger = self._initialize_logger()

    def _initialize_logger(self) -> logging.Logger:
        """
        Initialize a logger with the solver's name.
        """
        logger = logging.getLogger(self.LOGGER_NAME)
        return logger

    def __str__(self) -> str:
        return self.name

    def get_remaining_time(self) -> float:
        self.timeout_error()
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
            self.logger.warning(f"Timed out after {elapsed_time:.2f} seconds.")
            return True
        return False

    def timeout_error(self):
        if self.reach_timeout():
            raise TimeoutError()

    def time_solver(self, func):
        """
        Decorator to time a solver function.
        """

        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            self.solve_time = elapsed_time
            self.logger.info(
                f"Function {func.__name__:<40} took {elapsed_time:>8.4f} seconds"
            )
            return result

        return wrapper

    def time_pre_solve(self, func):
        """
        Decorator to time a solver function.
        """

        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            self.pre_solve_time = elapsed_time
            self.logger.info(
                f"Function {func.__name__:<40} took {elapsed_time:>8.4f} seconds"
            )
            return result

        return wrapper

    def solve(self, parameter: dict) -> dict:
        if not isinstance(self.graph, Graph_Wrapper):
            raise ValueError("Graph is not set. Please set the graph before solving.")
        self.logger.info(
            f"Starting {self.name} with parameters: {format_dictionary(parameter)}"
        )
        self.timeout = parameter["timeout"]
        self.start_time = time.time()
        ignore_degree = parameter.get("ignore_degree", False)
        if not ignore_degree and (not self.graph.check_degree_possible()):
            self.logger.warning("Failed: Graph does not meet degree constraints.")
            return {
                "success": False,
            }

        self.graph.name = self.name

        solution = self._actual_solver(parameter)
        self.logger.info("Completed.")
        return solution

    @abstractmethod
    def _actual_solver(self, parameter: dict) -> dict: ...

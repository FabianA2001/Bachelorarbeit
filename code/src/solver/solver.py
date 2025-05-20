from abc import ABC, abstractmethod
from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
import logging
from typing import Optional
import concurrent.futures


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

        if timeout != -1:
            try:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self._actual_solver)
                    result = future.result(timeout=timeout)
                    print("Ergebnis:", result)
            except concurrent.futures.TimeoutError:
                logging.info(
                    f"{self.name} hat das Zeitlimit von {timeout} Sekunden überschritten!"
                )
                result = False
        else:
            result = self._actual_solver()

        result = self._actual_solver()
        logging.info(f"{self.name} completed.")
        return result

    @abstractmethod
    def _actual_solver(self) -> bool: ...

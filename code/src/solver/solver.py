from abc import ABC, abstractmethod
from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
import logging
import multiprocessing
import queue


class Solver(ABC):
    """
    Abstract base class for all solvers.
    """

    def __init__(self, graph: Graph_Wrapper) -> None:
        self.name = "Solver"
        self.graph: Graph_Wrapper = graph
        self.success = False

    def handel_queue(self, result_queue) -> bool:
        if result_queue.empty():
            logging.warning("queue ist empty")
            self.success = False
            return False

        edges = []
        while not result_queue.empty():
            result = result_queue.get()
            if isinstance(result, list):
                if all(isinstance(i, tuple) for i in result):
                    edges = result
                    continue

            if isinstance(result, bool):
                self.success = result
                break

            assert False, "Result is not a tuple or bool, result: {}".format(result)

        if not len(edges) > 0:
            logging.warning("No edges found in queue")
            return self.success

        self.graph.clear_all_edges()
        for edge in edges:
            self.graph.add_edge(edge[0], edge[1], active=True)
        return self.success

    def __handel_solver_with_timeout(self, timeout: int) -> bool:
        result_queue = multiprocessing.Queue()
        process = multiprocessing.Process(
            target=self._actual_solver, args=(timeout, result_queue)
        )
        process.start()
        process.join(timeout if timeout > 0 else None)

        if process.is_alive():
            process.terminate()
            process.join()
            self.success = False
        return self.handel_queue(result_queue)

    def __handel_solver_without_timeout(self) -> bool:
        result_queue = queue.Queue()
        self._actual_solver(-1, result_queue)
        return self.handel_queue(result_queue)

    def solve(self, timeout: int = -1) -> bool:
        if not isinstance(self.graph, Graph_Wrapper):
            raise ValueError("Graph is not set. Please set the graph before solving.")
        logging.info(f"{self.name} started.")
        self.graph.name = self.name

        if timeout > 0:
            result = self.__handel_solver_with_timeout(timeout)
        else:
            result = self.__handel_solver_without_timeout()
        # if result:
        # print(*self.graph.get_all_edges(), sep="\n")
        logging.info(f"{self.name} completed.")
        return result

    @abstractmethod
    def _actual_solver(self, timeout, queue) -> None: ...

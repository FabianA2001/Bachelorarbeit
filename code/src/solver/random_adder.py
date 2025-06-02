from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from solver.solver import Solver
import random


class Random_Adder(Solver):
    VERSION = "0.1"

    def __init__(self, graph: Graph_Wrapper) -> None:
        super().__init__(graph)
        self.name = "random"

    def _actual_solver(self, timeout, queue) -> None:
        if not isinstance(self.graph, Graph_Wrapper):
            raise ValueError("Graph is not set. Please set the graph before solving.")
        self.graph.add_all_possible_edges(False)
        edges = self.graph.get_all_edges(False)
        final_edges = []
        while len(edges) > 0:
            edge = random.choice(edges)
            edges.remove(edge)
            self.graph.activate_edge(edge)
            if not self.graph.check_for_intersection_with_all_edges_and_nodes(edge):
                final_edges.append(edge)
            else:
                self.graph.deactivate_edge(edge)
        queue.put(final_edges)
        queue.put(True)

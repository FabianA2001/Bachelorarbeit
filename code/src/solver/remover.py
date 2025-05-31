from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from solver.solver import Solver
import logging


class Remover(Solver):
    def __init__(self, graph: Graph_Wrapper) -> None:
        logging.error("Remover ist noch nicht Fertig implementiert!")
        super().__init__(graph)
        self.name = "remover"
        self.version = "0.1"

    def _actual_solver(self, timeout, queue) -> None:
        if not isinstance(self.graph, Graph_Wrapper):
            raise ValueError("Graph is not set. Please set the graph before solving.")
        self.graph.add_all_possible_edges(True)

        nodes = self.graph.get_all_nodes_name()
        nodes = sorted(nodes, key=lambda n: self.graph.get_degree_of_node(n))
        for node in nodes:
            self.graph.show_and_save(show=False)
            edges = self.graph.get_edges_of_node(node)
            degree = self.graph.get_degree_of_node(node)
            for edge in edges:
                if len(edges) <= degree:
                    break
                if len(edges) == 0:
                    break
                if (
                    edge in self.graph.get_hull_edges()
                    or (edge[1], edge[0]) in self.graph.get_hull_edges()
                ):
                    continue
                if self.graph.check_for_intersection_with_all_edges_and_nodes(edge):
                    self.graph.deactivate_edge(edge)
            pass

        queue.put(self.graph.get_all_edges(True))
        queue.put(True)

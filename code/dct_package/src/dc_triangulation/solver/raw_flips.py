import random

from ..graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from ..solver.delaunay import Delaunay
from .solver import Solver


class Raw_Flips(Solver):
    NAME = "Raw_Flips"

    def __init__(self, graph: Graph_Wrapper) -> None:
        super().__init__(graph)
        self.name = self.NAME
        self.PROBABILITY = 0.2
        self.EXPONENT_ITERATIONS = 2

    def probability_check(self) -> bool:
        return self.PROBABILITY > random.random()

    def choose_edge(self, node: int) -> tuple[int, int]:
        if not isinstance(self.graph, Graph_Wrapper):
            raise ValueError("Graph is not set. Please set the graph before solving.")
        edges = self.graph.get_edges_of_node(node)
        if len(edges) == 0:
            self.graph.show_and_save(save=".")
            assert len(edges) > 0, "No edges found for node: {}".format(node)
        while len(edges) > 0:
            edge = random.choice(edges)
            edges.remove(edge)
            a, b = edge
            if a != node and not self.graph.check_node_for_degree(a):
                return edge
            if b != node and not self.graph.check_node_for_degree(b):
                return edge
            if self.probability_check():
                return edge

        # TODO Sehr unschön vlt bessere möglichkeit finden
        return edge

    def __do_flip(
        self,
    ) -> bool:
        if not isinstance(self.graph, Graph_Wrapper):
            raise ValueError("Graph is not set. Please set the graph before solving.")
        nodes = self.graph.get_all_nodes()
        for node in nodes:
            if self.graph.check_node_for_degree(node):
                continue
            edge = self.choose_edge(node)
            if not self.graph.flip_edge(edge):
                continue
            return True
        return False

    def _actual_solver(self, parameter: dict) -> dict:
        if not isinstance(self.graph, Graph_Wrapper):
            raise ValueError("Graph is not set. Please set the graph before solving.")

        solver = Delaunay(self.graph)
        self.graph.name = self.name
        solver.solve(parameter)

        for i in range(
            self.graph.get_number_edges_in_Triangulation() ** self.EXPONENT_ITERATIONS
        ):
            self.__do_flip()
            if not self.graph.check_if_triangulation_with_degree_constrained(
                check_degree=False
            ):
                self.graph.show_and_save(save=".")
                assert False, "Graph is not triangulated."
            if self.graph.check_if_triangulation_with_degree_constrained():
                return {
                    "success": True,
                }
            if i % 100 == 0:
                if self.reach_timeout():
                    return {
                        "success": False,
                    }

        return {
            "success": False,
        }

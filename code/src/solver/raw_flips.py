from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from solver.solver import Solver
from solver.delaunay import Delaunay
import random


class Raw_Flips(Solver):
    def __init__(self, graph: Graph_Wrapper) -> None:
        super().__init__(graph)
        self.name = "Raw_Flips"
        self.version = "0.1"
        self.PROBABILITY = 0.2
        self.EXPONENT_ITERATIONS = 2

    def probability_check(self) -> bool:
        return self.PROBABILITY > random.random()

    def choose_edge(self, node: str) -> tuple[str, str]:
        if not isinstance(self.graph, Graph_Wrapper):
            raise ValueError("Graph is not set. Please set the graph before solving.")
        edges = self.graph.get_edges_of_node(node)
        if len(edges) == 0:
            self.graph.show_and_save(show=False)
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
        nodes = self.graph.get_all_nodes_name()
        for node in nodes:
            if self.graph.check_node_for_degree(node):
                continue
            edge = self.choose_edge(node)
            if not self.graph.flip_edge(edge):
                continue
            return True
        return False

    def _actual_solver(self, timeout, queue) -> None:
        if not isinstance(self.graph, Graph_Wrapper):
            raise ValueError("Graph is not set. Please set the graph before solving.")

        solver = Delaunay(self.graph)
        self.graph.name = self.name
        solver.solve()

        for i in range(
            self.graph.get_number_edges_in_Triangulation() ** self.EXPONENT_ITERATIONS
        ):
            self.__do_flip()
            if not self.graph.check_if_triangulation_with_degree_constraint(
                check_degree=False
            ):
                self.graph.show_and_save()
                assert False, "Graph is not triangulated."
            if self.graph.check_if_triangulation_with_degree_constraint():
                queue.put(self.graph.get_all_edges())
                queue.put(True)
                return
            # einen Zwischenstand Speichern
            if i % self.graph.get_number_edges_in_Triangulation() == 0:
                queue.put(self.graph.get_all_edges())

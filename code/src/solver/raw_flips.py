from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from solver.solver import Solver
from solver.delaunay import Delaunay
import random


class Raw_Flips(Solver):
    def __init__(self, graph: Graph_Wrapper) -> None:
        super().__init__(graph)
        self.name = "Raw_Flips"

    def __do_flip(
        self,
    ) -> bool:
        if not isinstance(self.graph, Graph_Wrapper):
            raise ValueError("Graph is not set. Please set the graph before solving.")
        nodes = self.graph.get_all_nodes_name()
        for node in nodes:
            if self.graph.check_node_for_degree(node):
                continue
            edges = self.graph.get_edges_for_node(node)
            edge = random.choice(edges)
            if not self.graph.flip_edge(edge):
                continue
            return True
        return False

    def _actual_solver(self) -> bool:
        if not isinstance(self.graph, Graph_Wrapper):
            raise ValueError("Graph is not set. Please set the graph before solving.")

        self.graph.add_convex_hull()
        solver = Delaunay(self.graph)
        self.graph.name = self.name
        solver.solve()

        for _ in range(1000):
            self.__do_flip()
            if not self.graph.check_if_triangulation_with_degree_constraint(
                check_degree=False
            ):
                self.graph.show_and_save()
                assert False, "Graph is not triangulated."
            if self.graph.check_if_triangulation_with_degree_constraint():
                return True
        return False

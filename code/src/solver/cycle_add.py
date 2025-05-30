from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from solver.solver import Solver
import shapely


class Cycle_Add(Solver):
    def __init__(self, graph: Graph_Wrapper) -> None:
        super().__init__(graph)
        self.name = "Cycle_Add"
        self.version = "0.2"

    def sort_nodes_from_center(self) -> bool:
        """
        Sort the nodes in the graph based on their distance from the center of the graph.
        The center is defined as the average position of all nodes.
        """

        center_x, center_y = 0, 0
        for node in self.graph.get_all_nodes_name():
            point = self.graph.get_point_from_node(node)
            center_x += point.x
            center_y += point.y
        center = (
            center_x / len(self.graph.get_all_nodes_name()),
            center_y / len(self.graph.get_all_nodes_name()),
        )

        # Sort nodes based on their distance from the center
        sorted_nodes = sorted(
            self.graph.get_all_nodes_name(),
            key=lambda node: shapely.geometry.Point(center).distance(
                self.graph.get_point_from_node(node)
            ),
        )
        self.sorted_nodes = sorted_nodes
        return True

    def _actual_solver(self, timeout, queue) -> None:
        assert (
            self.graph.get_all_edges() == []
        ), "Graph is not empty. Please clear the graph before solving."
        self.graph.add_all_possible_edges(default_for_active=False)
        self.sort_nodes_from_center()
        quere_edges = []
        for node in reversed(self.sorted_nodes):
            edges = self.graph.get_edges_of_node(node)
            for edge in edges:
                self.graph.activate_edge(edge)
                if self.graph.check_for_intersection_with_all_edges_and_nodes(
                    edge, check_if_active=True
                ):
                    self.graph.deactivate_edge(edge)
                    continue
                if node != edge[0] and self.graph.check_node_for_degree(edge[0]):
                    self.graph.deactivate_edge(edge)
                    continue
                if node != edge[1] and self.graph.check_node_for_degree(edge[1]):
                    self.graph.deactivate_edge(edge)
                    continue
                quere_edges.append(edge)
        queue.put(quere_edges)
        queue.put(self.graph.check_if_triangulation_with_degree_constraint())
        return

from ..graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from .solver import Solver


class Greedy(Solver):
    NAME = "Greedy"

    def __init__(self, graph: Graph_Wrapper) -> None:
        super().__init__(graph)
        self.logger.warning("Kein Timeout")
        self.name = self.NAME

    def _actual_solver(self, parameter: dict) -> dict:
        if self.graph is None:
            raise ValueError("Graph is not set. Please set the graph before solving.")

        assert self.graph.get_all_edges() == [], (
            "Graph is not empty. Please clear the graph before solving."
        )

        # Get all nodes
        nodes_name = self.graph.get_all_nodes()
        self.logger.info(f"Starting greedy triangulation with {len(nodes_name)} nodes")

        self.graph.add_all_possible_edges(False)

        # Sort edges by distance (greedy approach: shortest edges first)
        potential_edges = [
            (self.graph.get_line_of_edge(edge).length, edge)
            for edge in self.graph.get_all_edges(test_active=False)
        ]
        potential_edges.sort(key=lambda x: x[0])

        # Greedily add edges
        added_edges = 0
        for i, (_, edge) in enumerate(potential_edges):
            # Check timeout periodically
            if i % 100 == 0 and self.reach_timeout():
                self.logger.warning("Timeout reached during greedy triangulation")
                return {"success": False}

            # Check if edge would intersect with existing edges
            if not self.graph.check_for_intersection_with_all_edges_and_nodes(edge):
                self.graph.activate_edge(edge)
                added_edges += 1

        self.logger.info(f"Greedy triangulation completed with {added_edges} edges")

        return {"success": True, "edges_added": added_edges}

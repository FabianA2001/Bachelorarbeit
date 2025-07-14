import itertools
import math

from ..graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from .solver import Solver


class Greedy(Solver):
    NAME = "Greedy"

    def __init__(self, graph: Graph_Wrapper) -> None:
        super().__init__(graph)
        self.logger.warning("Kein Timeout")
        self.name = self.NAME

    def _calculate_distance(
        self, pos1: tuple[int, int], pos2: tuple[int, int]
    ) -> float:
        """Calculate Euclidean distance between two points."""
        return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

    def _actual_solver(self, parameter: dict) -> dict:
        if self.graph is None:
            raise ValueError("Graph is not set. Please set the graph before solving.")

        assert self.graph.get_all_edges() == [], (
            "Graph is not empty. Please clear the graph before solving."
        )

        # Get all nodes
        nodes_name = self.graph.get_all_nodes()
        self.logger.info(f"Starting greedy triangulation with {len(nodes_name)} nodes")

        # Generate all possible edges with their distances
        potential_edges = []
        for node1, node2 in itertools.combinations(nodes_name, 2):
            pos1 = self.graph.get_pos_from_node(node1)
            pos2 = self.graph.get_pos_from_node(node2)
            distance = self._calculate_distance(pos1, pos2)
            potential_edges.append((distance, node1, node2))

        # Sort edges by distance (greedy approach: shortest edges first)
        potential_edges.sort(key=lambda x: x[0])
        self.logger.info(f"Generated {len(potential_edges)} potential edges")

        # Greedily add edges
        added_edges = 0
        for i, (distance, node1, node2) in enumerate(potential_edges):
            # Check timeout periodically
            if i % 100 == 0 and self.reach_timeout():
                self.logger.warning("Timeout reached during greedy triangulation")
                return {"success": False}

            # Try to add the edge
            edge = (node1, node2)

            # Check if edge would intersect with existing edges
            if not self.graph.check_for_intersection_with_all_edges_and_nodes(edge):
                self.graph.add_edge(node1, node2)
                added_edges += 1

        self.logger.info(f"Greedy triangulation completed with {added_edges} edges")

        return {"success": True, "edges_added": added_edges}

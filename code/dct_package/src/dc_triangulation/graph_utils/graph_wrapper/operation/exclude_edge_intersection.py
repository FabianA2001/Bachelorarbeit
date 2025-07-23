from collections import defaultdict

from ..data import Data


class Exclude_Edge_Intersection:
    def __init__(
        self, data: Data, intersections: dict[tuple[int, int], set[tuple[int, int]]]
    ) -> None:
        self.data = data
        self.intersections = intersections

    def __call__(self) -> set[tuple[int, int]]:
        return self.exclude_edge()

    def test_edge(self, edge: tuple[int, int]) -> bool:
        node_counter = defaultdict(int)
        for intersection in self.intersections.get(edge, []):
            assert intersection != []
            for node in intersection:
                node_counter[node] += 1

        for node in node_counter:
            if (
                self.data.degree(node) - node_counter[node]
                < self.data.nodes[node]["degree"]
            ):
                print("-----------------", node, "----", edge)
                return True
        return False

    def exclude_edge(self) -> set[tuple[int, int]]:
        edges = set()
        for edge in self.data.get_all_edges():
            if self.test_edge(edge):
                edges.add(edge)

        return edges

import itertools

import shapely

from ..data import Data


class Exclude_Edge_Partition:
    def __init__(
        self,
        data: Data,
        impossible_edges: list[tuple[int, int]],
    ) -> None:
        self.data = data
        self.hull_edges = self.data.get_hull_edges
        self.hull_nodes = self.data.get_hull_nodes_sorted
        self.impossible = impossible_edges
        self.points = [
            self.data.get_point_from_node(node)
            for node in self.data.get_all_nodes_name
            if node not in self.hull_nodes
        ]

    def __call__(self) -> list[tuple[int, int]]:
        return self.exclude_edge()

    def find_nodes_in_polygon(self, poly_nodes: list[int]) -> list[int]:
        polygon = shapely.geometry.Polygon(
            [self.data.get_point_from_node(node) for node in poly_nodes]
        )
        if not polygon.is_valid:
            return []
        if polygon.is_empty:
            return []
        points_in_polygon = [point for point in self.points if polygon.contains(point)]
        # Add the exterior points
        return [self.data.get_node_from_point(point) for point in points_in_polygon]

    def __possible_half(self, poly_nodes: list[int], exclude_nodes: list[int]) -> bool:
        nodes_in_polygon = self.find_nodes_in_polygon(poly_nodes)
        all_nodes = poly_nodes + nodes_in_polygon
        length = len(all_nodes)
        degree_sum = 0
        for node in all_nodes:
            if node in exclude_nodes:
                continue
            degree = self.data.nodes[node]["degree"]
            if degree > length - 1:
                return False
            degree_sum += degree
        for node in exclude_nodes:
            degree = self.data.nodes[node]["degree"]
            degree_sum += degree
        num_edges = 3 * len(all_nodes) - 3 - len(poly_nodes)
        if degree_sum < 2 * num_edges:
            return False
        return True

    def __degree_split_possible(
        self, poly1_nodes: list[int], poly2_nodes: list[int], a: int, b: int
    ) -> bool:
        nodes1 = self.find_nodes_in_polygon(poly1_nodes) + poly1_nodes
        degree_sum_1 = sum(
            self.data.nodes[node]["degree"]
            for node in nodes1
            if node != a and node != b
        )
        nodes2 = self.find_nodes_in_polygon(poly2_nodes) + poly2_nodes
        degree_sum_2 = sum(
            self.data.nodes[node]["degree"]
            for node in nodes2
            if node != a and node != b
        )
        num_edges_1 = 3 * len(nodes1) - 3 - len(poly1_nodes)
        num_edges_2 = 3 * len(nodes2) - 3 - len(poly2_nodes)

        x1 = degree_sum_2 - 2 * num_edges_2
        x2 = degree_sum_1 - 2 * num_edges_1

        if x1 < 2 or x2 < 2:
            # das kann nicht sein; mindestens 2 Kanten sind immer da
            return True

        if x1 == 2:
            return len(nodes1) != 3

        if x2 == 2:
            return len(nodes2) != 3

        # y1 = 2 * num_edges_1 - degree_sum_1 - 2
        # y2 = (
        #     degree_sum_2
        #     + self.data.nodes[a]["degree"]
        #     + self.data.nodes[b]["degree"]
        #     - 2 * num_edges_2
        # )
        # if y1 != y2:
        #     assert y1 >= 0, f"y1 and y2 must be non-negative for {a, b} split"
        #     assert (
        #         y1 <= self.data.nodes[a]["degree"] + self.data.nodes[b]["degree"] - 2
        #     ), "y1 and y2 must be less than the sum of the degrees of a and b minus 2"
        #     return False

        return True

    def __triangulate_half(self) -> bool:
        return True

    def exclude_edge(self) -> list[tuple[int, int]]:
        edges = set()
        for com in itertools.combinations(self.hull_nodes, 2):
            com = tuple(sorted(com))
            if com in self.impossible:
                continue
            if com in self.hull_edges:
                continue
            index0 = self.hull_nodes.index(com[0])
            index1 = self.hull_nodes.index(com[1])
            if index0 > index1:
                index0, index1 = index1, index0

            poly_nodes_0 = self.hull_nodes[index1:] + self.hull_nodes[: index0 + 1]
            poly_nodes_1 = self.hull_nodes[index0 : index1 + 1]
            # for half in [poly_nodes_0, poly_nodes_1]:
            #     if not self.__possible_half(half, [com[0], com[1]]):
            #         edges.add((min(com[0], com[1]), max(com[0], com[1])))
            #         continue

            # TODO liefert keine Ergebnis
            if not self.__degree_split_possible(
                poly_nodes_0, poly_nodes_1, com[0], com[1]
            ):
                # edges.add((min(com[0], com[1]), max(com[0], com[1])))
                continue

        # for node1, node2, node3 in zip(
        #     self.hull_nodes,
        #     self.hull_nodes[1:] + self.hull_nodes[:-1],
        #     self.hull_nodes[2:] + self.hull_nodes[:-2],
        # ):
        #     if self.data.nodes[node2]["degree"] != 2:
        #         edges.add((min(node1, node3), max(node1, node3)))

        return list(edges)

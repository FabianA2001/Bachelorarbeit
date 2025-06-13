from graph_utils.graph_wrapper.data import Data
import itertools
import shapely


class Exclude_Edge_Partition:
    def __init__(self, data: Data) -> None:
        self.data = data
        self.hull_edges = self.data.get_hull_edges
        self.hull_nodes = [edge[0] for edge in self.hull_edges]
        self.points = [
            self.data.get_point_from_node(node)
            for node in self.data.get_all_nodes_name
            if node not in self.hull_nodes
        ]

    def __call__(self) -> list[tuple[int, int]]:
        return self.exclude_edge()

    def __possible_half(self, poly_nodes: list[int], exclude_nodes: list[int]) -> bool:
        polygon = shapely.geometry.Polygon(
            [self.data.get_point_from_node(node) for node in poly_nodes]
        )
        if not polygon.is_valid:
            return True
        if polygon.is_empty:
            raise ValueError("Polygon is empty.")
        points_in_polygon = [point for point in self.points if polygon.contains(point)]
        # Add the exterior points
        nodes_in_polygon = [
            self.data.get_node_from_point(point) for point in points_in_polygon
        ]
        all_nodes = poly_nodes + nodes_in_polygon
        length = len(all_nodes)
        degree_sum = 0
        for node in all_nodes:
            if node in exclude_nodes:
                continue
            degree = self.data.nodes[node]["degree"]
            if degree > length:
                return False
            degree_sum += degree
        num_edges = 3 * len(all_nodes) - 3 - len(poly_nodes)
        if degree_sum != 2 * num_edges:
            return False
        return True

    def __triangulate_half(self) -> bool:
        return True

    def exclude_edge(self) -> list[tuple[int, int]]:
        edges = set()
        for com in itertools.combinations(self.hull_nodes, 2):
            if com in self.hull_edges or (com[1], com[0]) in self.hull_edges:
                continue
            index0 = self.hull_nodes.index(com[0])
            index1 = self.hull_nodes.index(com[1])
            if index0 > index1:
                index0, index1 = index1, index0

            poly_nodes_0 = self.hull_nodes[index1:] + self.hull_nodes[: index0 + 1]
            poly_nodes_1 = self.hull_nodes[index0 : index1 + 1]
            for half in [poly_nodes_0, poly_nodes_1]:
                if not self.__possible_half(half, [com[0], com[1]]):
                    edges.add(com)

        return list(edges)

from graph_utils.node import Node
import shapely
import itertools
import math
from graph_utils.graph_wrapper.data_raw import Data_Raw


class Data(Data_Raw):
    def __init__(self, nodes: list[Node]) -> None:
        super().__init__(nodes)
        self.number_edges_in_Triangulation = self.get_number_edges_triangulation()

    def get_number_edges_triangulation(self) -> int:
        """Gibt die Anzahl der Kanten im Graphen zurück."""
        k = len(self.get_hull_edges())
        n = len(self.get_all_nodes_name())
        # Aus Computational Geometry - Algorithms and Applications Seite 192
        return 3 * n - 3 - k

    def get_hull_points(self) -> list[shapely.Point]:
        points = [attr["point"] for _, attr in self.nodes(data=True)]
        convex_hull = shapely.geometry.MultiPoint(points).convex_hull
        if not isinstance(convex_hull, shapely.geometry.Polygon):
            raise ValueError("Convex hull is not a polygon.")
        outer_points = convex_hull.exterior.intersection(
            shapely.geometry.MultiPoint(points)
        )
        if not isinstance(outer_points, shapely.geometry.MultiPoint):
            raise ValueError("Intersection is not a MultiPoint.")
        return [node for node in outer_points.geoms]

    def get_hull_nodes(self) -> list[str]:
        return [self.get_node_from_point(node) for node in self.get_hull_points()]

    def get_hull_edges(self) -> list[tuple[str, str]]:
        def sorted_nodes(nodes: list[shapely.Point]) -> list[shapely.Point]:
            """Sortiert die Punkte im Uhrzeigersinn."""
            # Berechne den Schwerpunkt (Centroid) der Punkte
            center = shapely.geometry.MultiPoint(nodes).centroid

            # Berechne den Winkel jedes Punktes relativ zum Schwerpunkt
            def angle_from_center(point: shapely.Point) -> float:
                dx = point.x - center.x
                dy = point.y - center.y
                return math.atan2(dy, dx)  # Winkel in Bogenmaß

            # Sortiere die Punkte basierend auf den Winkeln im Uhrzeigersinn
            return sorted(nodes, key=angle_from_center, reverse=True)

        nodes = self.get_hull_points()
        nodes = sorted_nodes(nodes)
        edges = []
        for i in range(len(nodes)):
            edges.append(
                (
                    self.get_node_from_point(nodes[i]),
                    self.get_node_from_point(nodes[(i + 1) % len(nodes)]),
                )
            )
        return edges

    def get_triangles_for_node(self, node: str) -> list[str]:
        """Gibt die Dreiecke des Graphen zurück."""
        triangles = []
        neighbors = set(self[node])
        for u, v in itertools.combinations(neighbors, 2):
            if self.has_edge(u, v):
                triangles.append(tuple(sorted([node, u, v])))
        return triangles

    def get_triangles_for_edge(
        self, edge: tuple[str, str], check_active: bool = True
    ) -> list[tuple[str, str, str]]:
        """Gibt die Dreiecke des Graphen zurück."""
        triangles = []
        node1, node2 = edge
        neighbors1 = set(self[node1])
        neighbors2 = set(self[node2])
        for u in neighbors1.intersection(neighbors2):
            if not self.has_edge(node1, u):
                continue
            if not self.has_edge(node2, u):
                continue
            if check_active and not self.is_edge_active((node2, u)):
                continue
            if check_active and not self.is_edge_active((node1, u)):
                continue
            triangles.append(tuple(sorted([node1, node2, u])))
        return triangles

    def get_edges_for_node(self, node: str) -> list[tuple[str, str]]:
        """Gibt die Kanten des Graphen zurück."""
        return [(node, neighbor) for neighbor in self[node]]

    def get_all_triangles(self) -> list[tuple[str, str, str]]:
        """Gibt alle Dreiecke des Graphen zurück."""
        triangles = set()
        for node in self.get_all_nodes_name():
            for tri in self.get_triangles_for_node(node):
                triangles.add(tri)
        return list(triangles)

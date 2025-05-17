import networkx as nx
import matplotlib.pyplot as plt
from graph_utils import graph_const
from graph_utils.node import Node, save_nodes_as_json
import shapely
import itertools
from typing import Tuple, Union, Optional
import logging
import math


class Graph_Wrapper(nx.Graph):
    def __init__(self, nodes: list[Node]) -> None:
        super().__init__()
        self.given_nodes = nodes
        self.graph_name: str = graph_const.GRAPH_NAME
        for node in nodes:
            self.add_node(node.name, node.pos, node.degree)
        self.point_to_node: dict[shapely.Point, str] = {
            attr["point"]: node for node, attr in self.nodes(data=True)
        }
        self.number_edges_in_Triangulation = self.__get_number_edges_triangulation()

    def copy(self) -> "Graph_Wrapper":
        graph = Graph_Wrapper(self.given_nodes)
        for edge in self.get_all_edges():
            graph.add_edge(edge[0], edge[1], self.edges[edge].get("active"))
        return graph

    def get_aktive_graph(self) -> "Graph_Wrapper":
        local_graph = self.copy()
        for edge in local_graph.edges:
            if local_graph.edges[edge].get("active") is False:
                local_graph.remove_edge(edge)
        return local_graph

    def degree(self, node):
        return super().degree(node)  # type:ignore

    def add_node(self, key: str, pos: tuple[int, int], degree: int) -> None:
        """Fügt einen Knoten zum Graphen hinzu."""
        assert isinstance(pos, tuple), f"Erwarte Tuple, aber erhalte {type(pos)}, {pos}"
        super().add_node(key, pos=pos, degree=degree, point=shapely.geometry.Point(pos))

    def check_for_intersection_except_corners(
        self,
        line1: shapely.geometry.LineString | tuple[str, str],
        line2: shapely.geometry.LineString | tuple[str, str],
    ) -> bool:
        if isinstance(line1, tuple):
            line1 = self.edges[line1].get("line")
        if isinstance(line2, tuple):
            line2 = self.edges[line2].get("line")

        corner_points = [self.nodes[node].get("point") for node in self.nodes]
        intersection = line1.intersection(line2)  # type: ignore
        if intersection.is_empty:
            return False
        # Überprüfen, ob der Schnittpunkt einer der Eckpunkte ist
        if isinstance(intersection, shapely.geometry.Point):
            return intersection not in corner_points
        else:
            return True

    # Kantenfarben basierend auf einer Bedingung erstellen (z. B. Länge der Kante)

    def check_for_intersection_with_all_edges_and_nodes(
        self,
        edge: Union[tuple[str, str], shapely.LineString],
        check_if_active: bool = True,
    ) -> bool:
        """Überprüft, ob eine Linie mit einer anderen Linie im Graphen schneidet."""
        if isinstance(edge, tuple):
            if check_if_active:
                if not self.edges[edge].get("active"):
                    return False
            line = self.edges[edge].get("line")
        elif isinstance(edge, shapely.LineString):
            line = edge
        else:
            raise ValueError("Erwarte Tuple oder LineString")

        points = [self.nodes[node].get("point") for node in self.nodes]
        multipoint = shapely.geometry.MultiPoint(points)
        intersection = multipoint.intersection(line)
        if not isinstance(intersection, shapely.geometry.MultiPoint):
            raise ValueError(
                f"Intersection is not a MultiPoint, but {type(intersection)}"
            )
        if len(intersection.geoms) > 2:
            return True

        # Überprüfen, ob die Linie mit einer anderen Linie im Graphen schneidet
        all_linestrings_from_edges = [
            self.edges[edge].get("line")
            for edge in self.edges
            if self.edges[edge].get("active") or not check_if_active
        ]
        for other in all_linestrings_from_edges:
            if line == other:
                continue
            if self.check_for_intersection_except_corners(line, other):
                return True

        return False

    def show_and_save(self, show: bool = True, save: bool = True) -> None:
        """Zeichnet den Graphen mit den festgelegten Positionen und Farben."""
        logging.info("starte show_and_save")
        local_graph = self.get_aktive_graph()
        num_active_edges = len(local_graph.edges)
        # logging.info(f"aktive kanten: {num_active_edges}")
        print(local_graph.edges)
        if num_active_edges != self.number_edges_in_Triangulation:
            logging.error(
                f"Anzahl der Kanten in der Triangulation stimmt nicht überein.\nEs sollten {self.number_edges_in_Triangulation} sein, aber es sind {num_active_edges}."
            )
            save_graph_as_json(self, self.graph_name + "_error")

        pos = nx.get_node_attributes(local_graph, "pos")
        degrees = nx.get_node_attributes(local_graph, "degree")

        # Labels mit Degree-Werten erstellen
        labels = {node: f"{node}\n{degree}" for node, degree in degrees.items()}

        # Knotenfarben basierend auf dem Grad erstellen
        colors = [
            graph_const.NODE_COLOR_TRUE
            if degree
            == local_graph.degree(
                # type: ignore
                node
            )
            else graph_const.NODE_COLOR_FALSE
            for node, degree in degrees.items()
        ]

        edge_colors = [
            graph_const.EDGE_COLOR_TRUE
            # Beispielbedingung
            if not self.check_for_intersection_with_all_edges_and_nodes(edge)
            else graph_const.EDGE_COLOR_FALSE
            for edge in local_graph.edges
        ]

        # Zeichne den Graphen
        plt.clf()
        nx.draw(
            local_graph,
            pos=pos,
            labels=labels,
            node_color=colors,
            edge_color=edge_colors,  # Kantenfarben hier festlegen
            node_size=graph_const.NODE_SIZE,
            font_size=graph_const.FONT_SIZE,
        )
        plt.title("Graph mit festen Koordinaten")
        if save:
            plt.savefig(f"{graph_const.FIGURES_PREFIX}{self.graph_name}.pdf")
        if show:
            logging.info("show Graph")
            plt.show()
        logging.info("ende show_and_save")

    def add_edge(self, node1: str, node2: str, active: bool = True) -> None:
        """Fügt eine Kante zwischen zwei Knoten hinzu."""
        assert node1 in self and node2 in self
        super().add_edge(
            node1,
            node2,
            line=shapely.geometry.LineString(
                [self.nodes[node1]["point"], self.nodes[node2]["point"]]
            ),
            active=active,
        )

    def remove_edge(self, edge: tuple[str, str]) -> None:
        """Entfernt eine Kante zwischen zwei Knoten."""
        node1, node2 = edge
        assert node1 in self and node2 in self
        if (node1, node2) in self.edges:
            super().remove_edge(node1, node2)
        else:
            raise ValueError(f"Edge ({node1}, {node2}) not found in graph.")

    def active_edge(
        self, node1: Union[str, Tuple[str, str]], node2: Optional[str] = None
    ) -> None:
        """Aktiviert eine Kante zwischen zwei Knoten."""
        if node2 is None:
            if (
                isinstance(node1, tuple)
                and len(node1) == 2
                and all(isinstance(x, str) for x in node1)
            ):
                node1, node2 = node1
            else:
                raise ValueError("Erwarte Tuple[str, str]")
        else:
            if not isinstance(node1, str) or not isinstance(node2, str):
                raise ValueError("Beide Werte müssen Strings sein.")

        assert (node1, node2) in self.edges
        self.edges[node1, node2]["active"] = True

    def deactivate_edge(
        self, node1: Union[str, Tuple[str, str]], node2: Optional[str] = None
    ) -> None:
        """Deaktiviert eine Kante zwischen zwei Knoten."""
        if node2 is None:
            if (
                isinstance(node1, tuple)
                and len(node1) == 2
                and all(isinstance(x, str) for x in node1)
            ):
                node1, node2 = node1
            else:
                raise ValueError("Erwarte Tuple[str, str]")
        else:
            if not isinstance(node1, str) or not isinstance(node2, str):
                raise ValueError("Beide Werte müssen Strings sein.")

        assert (node1, node2) in self.edges
        self.edges[node1, node2]["active"] = False

    def add_all_possible_edges(self, default_for_active: bool = False) -> None:
        """Fügt alle möglichen Kanten zwischen den Knoten hinzu."""
        combinations = list(itertools.combinations(self.nodes, 2))
        for com in combinations:
            self.add_edge(com[0], com[1], default_for_active)

    def get_all_edges(self, test_active: bool = False) -> list[tuple[str, str]]:
        """Gibt alle Kanten des Graphen zurück."""
        all_edges = list(self.edges)
        if not test_active:
            return all_edges
        else:
            return [edge for edge in all_edges if self.edges[edge].get("active")]

    def get_all_nodes_name(self) -> list[str]:
        """Gibt alle Knoten des Graphen zurück."""
        return list(self.nodes)

    def get_node_from_point(self, point: shapely.Point) -> str:
        """Gibt den Knoten zurück, der dem gegebenen Punkt am nächsten ist."""
        if not isinstance(point, shapely.Point):
            raise ValueError(f"Erwarte einen Punkt., aber erhalte {type(point)}")
        if point not in self.point_to_node:
            raise ValueError(f"Point {point} not found in point_to_node.")
        node = self.point_to_node.get(point)
        assert node is not None, f"Node for point {point} not found."
        return node

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

    def add_convex_hull(self) -> None:
        """Fügt den konvexen Rumpf der Punkte als Kante hinzu."""
        for edge in self.get_hull_edges():
            self.add_edge(edge[0], edge[1], True)

    def __get_number_edges_triangulation(self) -> int:
        """Gibt die Anzahl der Kanten im Graphen zurück."""
        k = len(self.get_hull_edges())
        n = len(self.get_all_nodes_name())
        # Aus Computational Geometry - Algorithms and Applications Seite 192
        return 3 * n - 3 - k

    def get_triangles_for_node(self, node: str) -> list[str]:
        """Gibt die Dreiecke des Graphen zurück."""
        triangles = []
        neighbors = set(self[node])
        for u, v in itertools.combinations(neighbors, 2):
            if self.has_edge(u, v):
                triangles.append(tuple(sorted([node, u, v])))
        return triangles

    def get_triangles_for_edge(
        self, edge: tuple[str, str]
    ) -> list[tuple[str, str, str]]:
        """Gibt die Dreiecke des Graphen zurück."""
        triangles = []
        node1, node2 = edge
        neighbors1 = set(self[node1])
        neighbors2 = set(self[node2])
        for u in neighbors1.intersection(neighbors2):
            if self.has_edge(node1, u) and self.has_edge(node2, u):
                triangles.append(tuple(sorted([node1, node2, u])))
        return triangles

    def get_all_triangles(self) -> list[tuple[str, str, str]]:
        """Gibt alle Dreiecke des Graphen zurück."""
        triangles = set()
        for node in self.get_all_nodes_name():
            for tri in self.get_triangles_for_node(node):
                triangles.add(tri)
        return list(triangles)

    def flip_edge(self, edge: tuple[str, str]) -> bool:
        def reduce_to_two_tri(
            triangles: list[tuple[str, str, str]],
        ) -> list[tuple[str, str, str]]:
            """Reduziert die Liste der Dreiecke auf zwei."""
            nodes = set()
            for tri in triangles:
                for node in tri:
                    if node != edge[0] and node != edge[1]:
                        nodes.add(node)
            points = [self.nodes[node].get("point") for node in nodes]

            # logging.warning("starte While Schleife")
            counter = 0
            while len(triangles) > 2:
                counter += 1
                if counter > 500:
                    raise ValueError("Zu viele Iterationen in reduce_to_two_tri.")
                for tri in triangles:
                    tri_points = [self.nodes[node].get("point") for node in tri]
                    poly = shapely.geometry.Polygon(tri_points)
                    if not poly.is_valid:
                        raise ValueError(f"Polygon {poly} is not valid.\n{tri_points}")
                    for node, point in zip(nodes, points):
                        if node in tri:
                            continue
                        if poly.contains(point):
                            triangles.remove(tri)
                            break
            return triangles

        """Flippt eine Kante im Graphen."""
        edge = self.is_edge_in_graph(edge)
        triangles = self.get_triangles_for_edge(edge)
        if len(triangles) <= 1:
            return False

        if len(triangles) > 2:
            triangles = reduce_to_two_tri(triangles)
        assert len(triangles) == 2, f"Edge {edge} is not a diagonal.\n{triangles}"

        triangle1, triangle2 = triangles
        for node in triangle1:
            if edge[0] != node and edge[1] != node:
                a = node
        for node in triangle2:
            if edge[0] != node and edge[1] != node:
                b = node
        edges = self.get_all_edges()
        if (a, b) in edges or (b, a) in edges:
            return False

        self.add_edge(a, b, True)
        self.deactivate_edge(edge)
        if self.check_for_intersection_with_all_edges_and_nodes((a, b), True):
            self.remove_edge((a, b))
            self.active_edge(edge)
            # logging.warning(
            #     f"({a},{b}) würde mit einer anderen Kante schneiden.")
            return False
        # logging.info(
        #     f"({a},{b}) wurde erfolgreich hinzugefügt und ({edge[0]},{edge[1]}) entfernt.")
        self.remove_edge(edge)
        return True

    def is_edge_in_graph(self, edge: tuple[str, str]) -> tuple[str, str]:
        """Überprüft, ob eine Kante im Graphen vorhanden ist."""
        if edge not in self.edges:
            edge = (edge[1], edge[0])
        if edge not in self.edges:
            raise ValueError(f"Edge {edge} not found in graph.")
        return edge

    def check_if_triangulation_with_degree_constraint(self) -> bool:
        """Überprüft, ob der Graph eine Triangulation ist."""
        lokal_graph = self.get_aktive_graph()
        edges = lokal_graph.get_all_edges()
        if len(edges) != self.number_edges_in_Triangulation:
            return False
        for edge in edges:
            if self.check_for_intersection_with_all_edges_and_nodes(edge):
                return False
        for node in self.get_all_nodes_name():
            if lokal_graph.nodes[node].get("degree") != lokal_graph.degree(node):
                return False
        return True


def save_graph_as_json(
    graph: Graph_Wrapper, filename: str = graph_const.DEFAULT_FILE_NAME
) -> None:
    local_graph = graph.get_aktive_graph()

    nodes = []
    for node in local_graph.nodes:
        nodes.append(Node(node, local_graph.nodes[node]["pos"], graph.degree(node)))
    save_nodes_as_json(nodes, filename)

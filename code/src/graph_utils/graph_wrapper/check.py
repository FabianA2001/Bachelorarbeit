import shapely
from typing import Union
from graph_utils.graph_wrapper.data import Data
from shapely.strtree import STRtree
from itertools import combinations
import logging


class Check:
    def __init__(self, data: Data) -> None:
        self.data = data
        self.multipoint = None

    @staticmethod
    def sign(x):
        """Return the sign of x as -1 or 1."""
        return (x > 0) - (x < 0)

    @staticmethod
    def orientation(p1, p2, p3):
        """Check if the turn from p1 to p2 to p3 is a left turn."""
        return Check.sign(
            (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0])
        )

    def get_multipoint_for_points(self) -> shapely.geometry.MultiPoint:
        if self.multipoint is None:
            points = [self.data.nodes[node].get("point") for node in self.data.nodes]
            self.multipoint = shapely.geometry.MultiPoint(points)
        return self.multipoint

    def check_for_intersection_except_corners(
        self,
        line1: shapely.geometry.LineString | tuple[str, str],
        line2: shapely.geometry.LineString | tuple[str, str],
    ) -> bool:
        if isinstance(line1, tuple):
            line1 = self.data.edges[line1].get("line")
        if isinstance(line2, tuple):
            line2 = self.data.edges[line2].get("line")

        if not isinstance(line1, shapely.geometry.LineString) or not isinstance(
            line2, shapely.geometry.LineString
        ):
            raise ValueError("Erwarte Tuple oder LineString")
        return line1.crosses(line2)

    def check_edge_intersection_with_nodes(
        self,
        edge: Union[tuple[str, str], shapely.LineString],
        check_if_active: bool = True,
    ) -> bool:
        """Überprüft, ob eine Linie mit einer anderen Linie im Graphen schneidet."""
        if isinstance(edge, tuple):
            if edge not in self.data.get_all_edges():
                raise ValueError(f"Edge {edge} is not in the graph.")
            line = self.data.edges[edge].get("line")
        elif isinstance(edge, shapely.LineString):
            line = edge
        else:
            raise ValueError("Erwarte Tuple oder LineString")

        multipoint = self.get_multipoint_for_points()

        intersection = multipoint.intersection(line)
        if not isinstance(intersection, shapely.geometry.MultiPoint):
            raise ValueError(
                f"Intersection is not a MultiPoint, but {type(intersection)}"
            )
        if len(intersection.geoms) > 2:
            return True

        return False

    def check_for_intersection_with_all_edges_and_nodes(
        self,
        edge: Union[tuple[str, str], shapely.LineString],
        check_if_active: bool = True,
    ) -> bool:
        """Überprüft, ob eine Linie mit einer anderen Linie im Graphen schneidet."""
        if isinstance(edge, tuple):
            if edge not in self.data.get_all_edges():
                raise ValueError(f"Edge {edge} is not in the graph.")
            line = self.data.edges[edge].get("line")
        elif isinstance(edge, shapely.LineString):
            line = edge
        else:
            raise ValueError("Erwarte Tuple oder LineString")

        if self.check_edge_intersection_with_nodes(line, check_if_active):
            return True
            # Überprüfen, ob die Linie mit einer anderen Linie im Graphen schneidet
        lines = [
            self.data.edges[edge].get("line")
            for edge in self.data.edges
            if self.data.edges[edge].get("active") or not check_if_active
        ]
        # Baue spatial index
        tree = STRtree(lines)

        candidates = tree.query(line)
        for candidate in candidates:
            if line == lines[candidate]:
                continue
            if line.crosses(lines[candidate]):
                return True
        return False

    def get_intersections_with_all_edges_n2(
        self,
        edge: Union[tuple[str, str], shapely.LineString],
        check_if_active: bool = True,
    ) -> list[tuple[str, str]]:
        """Überprüft, ob eine Linie mit einer anderen Linie im Graphen schneidet."""
        if isinstance(edge, tuple):
            if edge not in self.data.get_all_edges():
                raise ValueError(f"Edge {edge} is not in the graph.")
            line = self.data.edges[edge].get("line")
        elif isinstance(edge, shapely.LineString):
            line = edge
        else:
            raise ValueError("Erwarte Tuple oder LineString")
        aktive_edges: list[tuple[str, str]] = [
            edge
            for edge in self.data.edges
            if self.data.edges[edge].get("active") or not check_if_active
        ]
        lines = [self.data.edges[edge].get("line") for edge in aktive_edges]
        # Baue spatial index

        edges = set()
        for edge, other_line in zip(aktive_edges, lines):
            if edge == line:
                continue
            if line.crosses(other_line):
                edges.add((min(edge[0], edge[1]), max(edge[0], edge[1])))

        return list(edges)

    def check_if_triangulation_with_degree_constraint(
        self, check_degree: bool = True, check_triangulation: bool = True
    ) -> bool:
        """Überprüft, ob der Graph eine Triangulation ist."""

        def __check_edges_for_intersection(lines) -> bool:
            # Baue spatial index
            tree = STRtree(lines)

            # Prüfe auf Schnitte
            for line in lines:
                # Nur mögliche Kandidaten holen
                candidates = tree.query(line)
                for candidate in candidates:
                    if line == lines[candidate]:
                        continue
                    if line.crosses(lines[candidate]):
                        return True

            return False

        lokal_graph = self.data.get_aktive_graph()
        if check_triangulation:
            edges = lokal_graph.get_all_edges()
            if len(edges) != self.data.number_edges_in_Triangulation:
                return False

            lines = [lokal_graph.edges[edge].get("line") for edge in edges]
            if __check_edges_for_intersection(lines):
                return False
        if check_degree:
            for node in self.data.get_all_nodes_name():
                if lokal_graph.nodes[node].get("degree") != lokal_graph.degree(node):
                    return False
        return True

    def get_all_intersections_n2(
        self, check_if_active: bool = True, timeout_func=lambda: ...
    ) -> set[tuple[tuple[str, str], tuple[str, str]]]:
        intersections = set()
        for edge1 in self.data.get_all_edges():
            for edge2 in self.data.get_all_edges():
                if edge1 == edge2:
                    continue
                if not self.data.edges[edge1].get("active") and check_if_active:
                    continue
                if not self.data.edges[edge2].get("active") and check_if_active:
                    continue
                if self.check_for_intersection_except_corners(edge1, edge2):
                    intersections.add(
                        (
                            min(min(edge1, edge2), max(edge1, edge2)),
                            max(min(edge1, edge2), max(edge1, edge2)),
                        )
                    )
        return intersections

    def get_all_intersections(
        self, check_if_active: bool = True, timeout_func=lambda: ...
    ) -> set[tuple[tuple[str, str], tuple[str, str]]]:
        """Gibt alle Kanten zurück, die sich schneiden."""
        if check_if_active:
            logging.warning("check_if_active is not implemented yet.")
        nodes = self.data.get_all_nodes_name()
        intersections = set()
        for node1, node2 in combinations(range(len(nodes)), 2):
            timeout_func()
            for current_node in range(len(nodes)):
                if current_node == node1 or current_node == node2:
                    continue

                orientation_node1_node2_current = self.orientation(
                    self.data.get_pos_from_node(nodes[node1]),
                    self.data.get_pos_from_node(nodes[node2]),
                    self.data.get_pos_from_node(nodes[current_node]),
                )
                for remaining_node in range(current_node + 1, len(nodes)):
                    if (
                        remaining_node == node1
                        or remaining_node == node2
                        or (node1, node2) < (current_node, remaining_node)
                    ):
                        # if remaining_node == node1 or remaining_node == node2:
                        continue  # make sure to not double count

                    orientation_node1_node2_remaining = self.orientation(
                        self.data.get_pos_from_node(nodes[node1]),
                        self.data.get_pos_from_node(nodes[node2]),
                        self.data.get_pos_from_node(nodes[remaining_node]),
                    )
                    # both points are on the same side of the line
                    if (
                        orientation_node1_node2_current
                        == orientation_node1_node2_remaining
                    ):
                        continue

                    orientation_current_remaining_node1 = self.orientation(
                        self.data.get_pos_from_node(nodes[current_node]),
                        self.data.get_pos_from_node(nodes[remaining_node]),
                        self.data.get_pos_from_node(nodes[node1]),
                    )
                    orientation_current_remaining_node2 = self.orientation(
                        self.data.get_pos_from_node(nodes[current_node]),
                        self.data.get_pos_from_node(nodes[remaining_node]),
                        self.data.get_pos_from_node(nodes[node2]),
                    )
                    # if the orientations are the same, the lines do not intersect
                    if (
                        orientation_current_remaining_node1
                        == orientation_current_remaining_node2
                    ):
                        continue

                    inter = (nodes[min(node1, node2)], nodes[max(node1, node2)])
                    inter2 = (
                        nodes[min(current_node, remaining_node)],
                        nodes[max(current_node, remaining_node)],
                    )
                    intersections.add((min(inter, inter2), max(inter, inter2)))
        return intersections

    def check_node_for_degree(self, node: str) -> bool:
        """Überprüft, ob der Knoten die richtige Anzahl an Nachbarn hat."""
        if node not in self.data.get_all_nodes_name():
            raise ValueError(f"Node {node} is not in the graph.")
        if self.data.nodes[node].get("degree") != self.data.degree(node):
            return False
        return True

import shapely
from typing import Union
from graph_utils.graph_wrapper.data import Data
from shapely.strtree import STRtree


class Check:
    def __init__(self, data: Data) -> None:
        self.data = data
        self.multipoint = None

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
            if check_if_active:
                if not self.data.edges[edge].get("active"):
                    return False
            line = self.data.edges[edge].get("line")
        elif isinstance(edge, shapely.LineString):
            line = edge
        else:
            raise ValueError("Erwarte Tuple oder LineString")

        multipoint = self.multipoint

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
            if check_if_active:
                if not self.data.edges[edge].get("active"):
                    return False
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

    def check_node_for_degree(self, node: str) -> bool:
        """Überprüft, ob der Knoten die richtige Anzahl an Nachbarn hat."""
        if node not in self.data.get_all_nodes_name():
            raise ValueError(f"Node {node} is not in the graph.")
        if self.data.nodes[node].get("degree") != self.data.degree(node):
            return False
        return True

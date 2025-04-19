import networkx as nx
import matplotlib.pyplot as plt
from graphe_utils import graphe_const
from graphe_utils.node import Node
import shapely
import itertools
from typing import Tuple, Union, Optional
import logging


class Graphe:
    def __init__(self, nodes: list[Node]) -> None:
        self.graph = nx.Graph()
        self.__positions: list[Node] = nodes
        self.name: str = graphe_const.GRAPHE_NAME
        for node in self.__positions:
            self.__add_node(node.name, node.pos, node.degree)

    def __add_node(self, key: str, pos: tuple[int, int], degree: int) -> None:
        """Fügt einen Knoten zum Graphen hinzu."""
        self.graph.add_node(
            key, pos=pos, degree=degree, point=shapely.geometry.Point(pos)
        )

    def check_for_intersection_ececpt_corners(
        self,
        line1: shapely.geometry.LineString | tuple[str, str],
        line2: shapely.geometry.LineString | tuple[str, str],
    ) -> bool:
        if isinstance(line1, tuple):
            line1 = self.graph.edges[line1].get("line")
        if isinstance(line2, tuple):
            line2 = self.graph.edges[line2].get("line")

        corner_points = [
            self.graph.nodes[node].get("point") for node in self.graph.nodes
        ]
        intersection = line1.intersection(line2)  # type: ignore
        if intersection.is_empty:
            return False
        # Überprüfen, ob der Schnittpunkt einer der Eckpunkte ist
        if isinstance(intersection, shapely.geometry.Point):
            return intersection not in corner_points
        else:
            return True

    # Kantenfarben basierend auf einer Bedingung erstellen (z. B. Länge der Kante)

    def check_for_intersection_with_all_edges(
        self, edge: tuple[str, str], check_if_active: bool = True
    ) -> bool:
        """Überprüft, ob eine Linie mit einer anderen Linie im Graphen schneidet."""
        if not self.graph.edges[edge].get("active") and check_if_active:
            return False
        line = self.graph.edges[edge].get("line")
        all_linestrings_from_edges = [
            self.graph.edges[edge].get("line")
            for edge in self.graph.edges
            if self.graph.edges[edge].get("active") or not check_if_active
        ]
        for other in all_linestrings_from_edges:
            if line == other:
                continue
            if self.check_for_intersection_ececpt_corners(line, other):
                return True
        return False

    def show_and_save(self) -> None:
        """Zeichnet den Graphen mit den festgelegten Positionen und Farben."""
        local_grphe = self.graph.copy()
        for edge in local_grphe.edges:
            if local_grphe.edges[edge].get("active") is False:
                local_grphe.remove_edge(edge[0], edge[1])

        logging.info(f"aktive kanten: {sum(1 for _ in local_grphe.edges)}")
        pos = nx.get_node_attributes(local_grphe, "pos")
        degrees = nx.get_node_attributes(local_grphe, "degree")

        # Labels mit Degree-Werten erstellen
        labels = {node: f"{node}\n{degree}" for node, degree in degrees.items()}

        # Knotenfarben basierend auf dem Grad erstellen
        colors = [
            graphe_const.NODE_COLOR_TRUE
            if degree
            == local_grphe.degree(
                # type: ignore
                node
            )
            else graphe_const.NODE_COLOR_FALSE
            for node, degree in degrees.items()
        ]

        edge_colors = [
            graphe_const.EDGE_COLOR_TRUE
            # Beispielbedingung
            if not self.check_for_intersection_with_all_edges(edge)
            else graphe_const.EDGE_COLOR_FALSE
            for edge in local_grphe.edges
        ]

        # Zeichne den Graphen
        nx.draw(
            local_grphe,
            pos=pos,
            labels=labels,
            node_color=colors,
            edge_color=edge_colors,  # Kantenfarben hier festlegen
            node_size=graphe_const.NODE_SIZE,
            font_size=graphe_const.FONT_SIZE,
        )
        plt.title("Graph mit festen Koordinaten")
        plt.savefig(f"{graphe_const.FIGURES_PREFIX}{self.name}.pdf")
        plt.show()

    def add_edge(self, node1: str, node2: str, value_active: bool = False) -> None:
        """Fügt eine Kante zwischen zwei Knoten hinzu."""
        assert node1 in self.graph and node2 in self.graph
        self.graph.add_edge(
            node1,
            node2,
            line=shapely.geometry.LineString(
                [self.graph.nodes[node1]["point"], self.graph.nodes[node2]["point"]]
            ),
            active=value_active,
        )

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

        assert (node1, node2) in self.graph.edges
        self.graph.edges[node1, node2]["active"] = True

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

        assert (node1, node2) in self.graph.edges
        self.graph.edges[node1, node2]["active"] = False

    def add_all_possible_edges(self, default_for_active: bool = False) -> None:
        """Fügt alle möglichen Kanten zwischen den Knoten hinzu."""
        combinations = list(itertools.combinations(self.graph.nodes, 2))
        for com in combinations:
            self.add_edge(com[0], com[1], default_for_active)

    def get_all_edges(self) -> list[tuple[str, str]]:
        """Gibt alle Kanten des Graphen zurück."""
        return list(self.graph.edges)

    def get_all_nodes(self) -> list[str]:
        """Gibt alle Knoten des Graphen zurück."""
        return list(self.graph.nodes)

import networkx as nx
import matplotlib.pyplot as plt
from graphe_utils import graphe_const
from graphe_utils.node import Node
import shapely


class Graphe:
    def __init__(self, positions: list[Node]) -> None:
        self.graph = nx.Graph()
        self.__positions: list[Node] = positions
        self.name: str = graphe_const.GRAPHE_NAME
        for node in self.__positions:
            self.__add_node(node.name, node.pos, node.degree)

    def __add_node(self, key: str, pos: tuple[int, int], degree: int) -> None:
        """Fügt einen Knoten zum Graphen hinzu."""
        self.graph.add_node(
            key, pos=pos, degree=degree, point=shapely.geometry.Point(pos)
        )

    # Kantenfarben basierend auf einer Bedingung erstellen (z. B. Länge der Kante)
    def check_for_intersection(self, line: shapely.geometry.LineString) -> bool:
        """Überprüft, ob eine Linie mit einer anderen Linie im Graphen schneidet."""
        all_Linestrings_from_edges = [
            self.graph.edges[edge].get("line") for edge in self.graph.edges
        ]
        for other in all_Linestrings_from_edges:
            if line.intersects(other) and line != other:
                return True
        return False

    def show_and_save(self) -> None:
        """Zeichnet den Graphen mit den festgelegten Positionen und Farben."""
        pos = nx.get_node_attributes(self.graph, "pos")
        degrees = nx.get_node_attributes(self.graph, "degree")

        # Labels mit Degree-Werten erstellen
        labels = {node: f"{node}\n{degree}" for node, degree in degrees.items()}

        # Knotenfarben basierend auf dem Grad erstellen
        colors = [
            graphe_const.NODE_COLOR_TRUE
            if degree
            == self.graph.degree(
                # type: ignore
                node
            )
            else graphe_const.NODE_COLOR_FALSE
            for node, degree in degrees.items()
        ]

        edge_colors = [
            graphe_const.EDGE_COLOR_TRUE
            # Beispielbedingung
            if not self.check_for_intersection(self.graph.edges[edge].get("line"))
            else graphe_const.EDGE_COLOR_FALSE
            for edge in self.graph.edges
        ]

        # Zeichne den Graphen
        nx.draw(
            self.graph,
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

    def add_edge(self, node1: str, node2: str) -> None:
        """Fügt eine Kante zwischen zwei Knoten hinzu."""
        assert node1 in self.graph and node2 in self.graph
        self.graph.add_edge(
            node1,
            node2,
            line=shapely.geometry.LineString(
                [self.graph.nodes[node1]["point"], self.graph.nodes[node2]["point"]]
            ),
        )

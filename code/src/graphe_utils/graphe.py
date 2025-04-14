import networkx as nx
import matplotlib.pyplot as plt
import logging
from graphe_utils import graphe_const
from graphe_utils.node import Node


class Graphe:
    def __init__(self, positions: list[Node]) -> None:
        self.graph = nx.Graph()
        self.__positions: list[Node] = positions
        self.name: str = graphe_const.GRAPHE_NAME
        for node in self.__positions:
            self.__add_node(node.name, node.pos, node.degree)

    def __add_node(self, key: str, pos: tuple[int, int], degree: int) -> None:
        """Fügt einen Knoten zum Graphen hinzu."""
        self.graph.add_node(key, pos=pos, degree=degree)

    def show_and_save(self) -> None:
        """Zeichnet den Graphen mit den festgelegten Positionen."""
        pos = nx.get_node_attributes(self.graph, 'pos')
        degrees = nx.get_node_attributes(self.graph, 'degree')
        # Labels mit Degree-Werten erstellen
        labels = {node: f"{node}\n{degree}" for node,
                  degree in degrees.items()}
        # Knotenfarben basierend ob der Grad errfüllt wurde erstellen
        colors = [graphe_const.NODE_COLOR_TRUE if degree == self.graph.degree(
            # type: ignore
            node) else graphe_const.NODE_COLOR_FALSE for node, degree in degrees.items()]
        nx.draw(self.graph, pos=pos, labels=labels,
                node_color=colors, node_size=graphe_const.NODE_SIZE, font_size=graphe_const.FONT_SIZE)
        plt.title("Graph mit festen Koordinaten")
        plt.savefig(f"{graphe_const.FIGURES_PREFIX}{self.name}.pdf")
        plt.show()

    def add_edge(self, node1: str, node2: str) -> None:
        """Fügt eine Kante zwischen zwei Knoten hinzu."""
        assert (node1 in self.graph and node2 in self.graph)
        self.graph.add_edge(node1, node2)

from typing import Dict
import networkx as nx
import matplotlib.pyplot as plt
import logging
import const


class Node:
    def __init__(self, name: str, pos: tuple[int, int], degree: int) -> None:
        self.name = name
        self.pos = pos
        self.degree = degree

    def __str__(self) -> str:
        return f"{self.name} ({self.pos[0]}, {self.pos[1]})"

    def __repr__(self) -> str:
        return f"Node({self.name}, {self.pos})"


class Graphe:
    def __init__(self, positions: list[Node]) -> None:
        self.graph = nx.Graph()
        self.__positions: list[Node] = positions
        self.name: str = const.GRAPHE_NAME
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
        colors = [const.NODE_COLOR_TRUE if degree == self.graph.degree(
            # type: ignore
            node) else const.NODE_COLOR_FALSE for node, degree in degrees.items()]
        nx.draw(self.graph, pos=pos, labels=labels,
                node_color=colors, node_size=const.NODE_SIZE)
        plt.title("Graph mit festen Koordinaten")
        plt.savefig(f"{const.FIGURES_PREFIX}{self.name}.pdf")
        plt.show()

    def add_edge(self, node1: str, node2: str) -> None:
        """Fügt eine Kante zwischen zwei Knoten hinzu."""
        if node1 not in self.graph or node2 not in self.graph:
            logging.error("Einer der Knoten existiert nicht.")
            return
        self.graph.add_edge(node1, node2)

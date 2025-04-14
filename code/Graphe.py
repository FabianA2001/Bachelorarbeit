from typing import Dict
import networkx as nx
import matplotlib.pyplot as plt
import logging
import const


class Graphe:
    def __init__(self, positions: Dict[str, tuple[int, int]]) -> None:
        self.graph = nx.Graph()
        self.__positions: Dict[str, tuple[int, int]] = positions
        self.name: str = const.GRAPHE_NAME
        for node, pos in self.__positions.items():
            self.__add_node(node, pos)

    def __add_node(self, key: str, pos: tuple[int, int]) -> None:
        """Fügt einen Knoten zum Graphen hinzu."""
        self.graph.add_node(key, pos=pos)

    def show_and_save(self) -> None:
        """Zeichnet den Graphen mit den festgelegten Positionen."""
        pos = nx.get_node_attributes(self.graph, 'pos')
        nx.draw(self.graph, pos=pos, with_labels=True,
                node_color=const.NODE_COLOR, node_size=const.NODE_SIZE)
        plt.title("Graph mit festen Koordinaten")
        plt.savefig(f"{const.FIGURES_PREFIX}{self.name}.pdf")
        plt.show()

    def add_edge(self, node1: str, node2: str) -> None:
        """Fügt eine Kante zwischen zwei Knoten hinzu."""
        if node1 not in self.graph or node2 not in self.graph:
            logging.error("Einer der Knoten existiert nicht.")
            return
        self.graph.add_edge(node1, node2)

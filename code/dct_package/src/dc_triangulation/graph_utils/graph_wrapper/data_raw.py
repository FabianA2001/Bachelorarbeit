from functools import cached_property
from typing import Optional, Tuple, Union

import networkx as nx
import shapely

from .. import graph_const
from ..node import Node


class Data_Raw(nx.Graph):
    def __init__(self, nodes: list[Node]) -> None:
        super().__init__()
        self.node_name = 0
        self.name: str = graph_const.GRAPH_NAME
        for node in nodes:
            self.add_node(node.pos, node.degree)
        self.point_to_node: dict[shapely.Point, int] = {
            attr["point"]: node for node, attr in self.nodes(data=True)
        }
        self.pos_to_node: dict[tuple[int, int], int] = {
            attr["pos"]: node for node, attr in self.nodes(data=True)
        }

    def add_node(self, pos: tuple[int, int], degree: int) -> None:
        """Fügt einen Knoten zum Graphen hinzu."""
        self.clear_cache()
        assert isinstance(pos, tuple), f"Erwarte Tuple, aber erhalte {type(pos)}, {pos}"
        super().add_node(
            self.node_name, pos=pos, degree=degree, point=shapely.geometry.Point(pos)
        )
        self.node_name += 1

    def get_node_from_point(self, point: shapely.Point) -> int:
        """Gibt den Knoten zurück, der einen bestimmten Punkt repräsentiert."""
        if not isinstance(point, shapely.Point):
            raise ValueError(f"Erwarte einen Punkt., aber erhalte {type(point)}")
        if point not in self.point_to_node:
            raise ValueError(f"Point {point} not found in point_to_node.")
        node = self.point_to_node.get(point)
        assert node is not None, f"Node for point {point} not found."
        return node

    def get_node_from_pos(self, pos: tuple[int, int]) -> int:
        """Gibt den Knoten zurück, der eine bestimmte Position repräsentiert."""
        if not isinstance(pos, tuple):
            raise ValueError(f"Erwarte ein Tuple, aber erhalte {type(pos)}")
        if pos not in self.pos_to_node:
            raise ValueError(f"Position {pos} not found in pos_to_node.")
        node = self.pos_to_node.get(pos)
        assert node is not None, f"Node for position {pos} not found."
        return node

    def get_point_from_node(self, node: int) -> shapely.Point:
        """Gibt den Punkt des Knotens zurück."""
        if node not in self.nodes:
            raise ValueError(f"Node {node} not found in graph.")
        point = self.nodes[node].get("point")
        if not isinstance(point, shapely.Point):
            raise TypeError(f"Point is not a shapely.Point, but {type(point)}")
        return point

    def get_pos_from_node(self, node: int) -> tuple[int, int]:
        """Gibt die Position des Knotens zurück."""
        if node not in self.nodes:
            raise ValueError(f"Node {node} not found in graph.")
        pos = self.nodes[node].get("pos")
        if not isinstance(pos, tuple):
            raise TypeError(f"Position is not a tuple, but {type(pos)}")
        return pos

    def copy(self) -> "Data_Raw":
        nodes = []
        for node in self.get_all_nodes_name:
            nodes.append(Node(self.nodes[node]["pos"], self.nodes[node]["degree"]))
        graph = Data_Raw(nodes)
        for edge in self.get_all_edges():
            graph.add_edge(edge[0], edge[1], self.edges[edge].get("active"))
        return graph

    # TODO löschen um sicher cache zu nutzen
    def get_all_edges(self, test_active: bool = False) -> list[tuple[int, int]]:
        """Gibt alle Kanten des Graphen zurück."""
        all_edges = list(self.edges)
        if not test_active:
            return all_edges
        else:
            return [edge for edge in all_edges if self.edges[edge].get("active")]

    def add_edge(self, node1: int, node2: int, active: bool = True) -> None:
        """Fügt eine Kante zwischen zwei Knoten hinzu."""
        self.clear_cache()
        assert node1 in self and node2 in self
        super().add_edge(
            node1,
            node2,
            line=shapely.geometry.LineString(
                [self.nodes[node1]["point"], self.nodes[node2]["point"]]
            ),
            active=active,
        )

    def remove_edge(self, edge: tuple[int, int]) -> None:
        """Entfernt eine Kante zwischen zwei Knoten."""
        self.clear_cache()
        node1, node2 = edge
        assert node1 in self and node2 in self
        if (node1, node2) in self.edges:
            # logging.info(f"Removing edge {edge}")
            super().remove_edge(node1, node2)
        else:
            raise ValueError(f"Edge ({node1}, {node2}) not found in graph.")

    def active_edge(
        self, node1: Union[int, Tuple[int, int]], node2: Optional[int] = None
    ) -> None:
        """Aktiviert eine Kante zwischen zwei Knoten."""
        self.clear_cache()
        if node2 is None:
            if (
                isinstance(node1, tuple)
                and len(node1) == 2
                and all(isinstance(x, int) for x in node1)
            ):
                node1, node2 = node1
            else:
                raise ValueError("Erwarte Tuple[int, int]")
        else:
            if not isinstance(node1, int) or not isinstance(node2, int):
                raise ValueError("Beide Werte müssen Strings sein.")

        assert (node1, node2) in self.edges
        self.edges[node1, node2]["active"] = True

    def deactivate_edge(
        self, node1: Union[int, Tuple[int, int]], node2: Optional[int] = None
    ) -> None:
        """Deaktiviert eine Kante zwischen zwei Knoten."""
        self.clear_cache()
        if node2 is None:
            if (
                isinstance(node1, tuple)
                and len(node1) == 2
                and all(isinstance(x, int) for x in node1)
            ):
                node1, node2 = node1
            else:
                raise ValueError("Erwarte Tuple[int, int]")
        else:
            if not isinstance(node1, int) or not isinstance(node2, int):
                raise ValueError("Beide Werte müssen Strings sein.")

        assert (node1, node2) in self.edges
        self.edges[node1, node2]["active"] = False

    def is_edge_active(self, edge: tuple[int, int]) -> bool:
        """Überprüft, ob eine Kante aktiv ist."""
        if edge not in self.edges:
            raise ValueError(f"Edge {edge} not found in graph.")
        return self.edges[edge].get("active")

    def get_aktive_graph(self) -> "Data_Raw":
        local_graph = self.copy()
        for edge in local_graph.edges:
            if local_graph.edges[edge].get("active") is False:
                local_graph.remove_edge(edge)
        return local_graph

    def degree(self, node):
        return super().degree(node)  # type:ignore

    def get_line_of_edge(self, edge: tuple[int, int]) -> shapely.LineString:
        """Gibt die Linie einer Kante zurück."""
        if edge not in self.edges:
            raise ValueError(f"Edge {edge} not found in graph.")
        return self.edges[edge]["line"]

    def degree_aktive(self, node: int) -> int:
        """Gibt den Grad eines Knotens im aktiven Graphen zurück."""
        if node not in self.nodes:
            raise ValueError(f"Node {node} not found in graph.")
        lokal = self.get_aktive_graph()
        return lokal.degree(node)

    def is_edge_in_graph(self, edge: tuple[int, int]) -> tuple[int, int]:
        if not isinstance(edge, tuple) or len(edge) != 2:
            raise ValueError(f"Erwarte Tuple aber erhalte {type(edge)}, {edge}")
        if not all(isinstance(x, int) for x in edge):
            raise ValueError(
                f"Erwarte Tuple mit Strings aber erhalte {type(edge)}, {edge}"
            )
        """Überprüft, ob eine Kante im Graphen vorhanden ist."""
        if edge not in self.edges:
            edge = (edge[1], edge[0])
        if edge not in self.edges:
            raise ValueError(f"Edge {edge} not found in graph.")
        return edge

    def clear_cache(self):
        """Leert den Cache der all_edges-Property."""
        for cls in self.__class__.__mro__:
            for name, attr in cls.__dict__.items():
                if isinstance(attr, cached_property):
                    self.__dict__.pop(name, None)

    @cached_property
    def all_edges(self) -> list[tuple[int, int]]:
        """Gibt alle Kanten des Graphen zurück."""
        return list(self.edges)

    @cached_property
    def all_edges_aktive(self) -> list[tuple[int, int]]:
        """Gibt alle aktiven Kanten des Graphen zurück."""
        return [edge for edge in self.edges if self.edges[edge].get("active", True)]

    @cached_property
    def get_all_nodes_name(self) -> list[int]:
        """Gibt alle Knoten des Graphen zurück."""
        return list(self.nodes)

    @cached_property
    def get_aktive_graph_nodes(self) -> list[Node]:
        nodes = []
        for node in self.get_all_nodes_name:
            nodes.append(Node(self.nodes[node]["pos"], self.degree_aktive(node)))

        return nodes

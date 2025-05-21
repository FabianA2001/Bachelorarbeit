import networkx as nx
from graph_utils import graph_const
from graph_utils.node import Node
import shapely
import itertools
from typing import Tuple, Union, Optional


class Data_Raw(nx.Graph):
    def __init__(self, nodes: list[Node]) -> None:
        super().__init__()
        self.name: str = graph_const.GRAPH_NAME
        for node in nodes:
            self.add_node(node.name, node.pos, node.degree)
        self.point_to_node: dict[shapely.Point, str] = {
            attr["point"]: node for node, attr in self.nodes(data=True)
        }

    def add_node(self, key: str, pos: tuple[int, int], degree: int) -> None:
        """Fügt einen Knoten zum Graphen hinzu."""
        assert isinstance(pos, tuple), f"Erwarte Tuple, aber erhalte {type(pos)}, {pos}"
        super().add_node(key, pos=pos, degree=degree, point=shapely.geometry.Point(pos))

    def get_all_nodes_name(self) -> list[str]:
        """Gibt alle Knoten des Graphen zurück."""
        return list(self.nodes)

    def get_node_from_point(self, point: shapely.Point) -> str:
        """Gibt den Knoten zurück, der einen bestimmten Punkt repräsentiert."""
        if not isinstance(point, shapely.Point):
            raise ValueError(f"Erwarte einen Punkt., aber erhalte {type(point)}")
        if point not in self.point_to_node:
            raise ValueError(f"Point {point} not found in point_to_node.")
        node = self.point_to_node.get(point)
        assert node is not None, f"Node for point {point} not found."
        return node

    def copy(self) -> "Data_Raw":
        nodes = []
        for node in self.get_all_nodes_name():
            nodes.append(
                Node(node, self.nodes[node]["pos"], self.nodes[node]["degree"])
            )
        graph = Data_Raw(nodes)
        for edge in self.get_all_edges():
            graph.add_edge(edge[0], edge[1], self.edges[edge].get("active"))
        return graph

    def get_all_edges(self, test_active: bool = False) -> list[tuple[str, str]]:
        """Gibt alle Kanten des Graphen zurück."""
        all_edges = list(self.edges)
        if not test_active:
            return all_edges
        else:
            return [edge for edge in all_edges if self.edges[edge].get("active")]

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
            # logging.info(f"Removing edge {edge}")
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

    def is_edge_active(self, edge: tuple[str, str]) -> bool:
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

    def get_aktive_graph_nodes(self) -> list[Node]:
        local_graph = self.get_aktive_graph()

        nodes = []
        for node in local_graph.nodes:
            nodes.append(Node(node, local_graph.nodes[node]["pos"], self.degree(node)))

        return nodes

    def is_edge_in_graph(self, edge: tuple[str, str]) -> tuple[str, str]:
        if not isinstance(edge, tuple) or len(edge) != 2:
            raise ValueError(f"Erwarte Tuple aber erhalte {type(edge)}, {edge}")
        if not all(isinstance(x, str) for x in edge):
            raise ValueError(
                f"Erwarte Tuple mit Strings aber erhalte {type(edge)}, {edge}"
            )
        """Überprüft, ob eine Kante im Graphen vorhanden ist."""
        if edge not in self.edges:
            edge = (edge[1], edge[0])
        if edge not in self.edges:
            raise ValueError(f"Edge {edge} not found in graph.")
        return edge

    def add_all_possible_edges(self, default_for_active: bool = False) -> None:
        """Fügt alle möglichen Kanten zwischen den Knoten hinzu."""
        combinations = list(itertools.combinations(self.nodes, 2))
        for com in combinations:
            self.add_edge(com[0], com[1], default_for_active)

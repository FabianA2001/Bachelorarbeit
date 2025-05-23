from graph_utils import graph_const
from graph_utils.node import Node
import shapely
from typing import Tuple, Union, Optional
from graph_utils.graph_wrapper.data import Data
from graph_utils.graph_wrapper.data_raw import Data_Raw
from graph_utils.graph_wrapper import check
from graph_utils.graph_wrapper import visualisation
from graph_utils.graph_wrapper.operation import flip_edge
from graph_utils.graph_wrapper.operation import move_node
from graph_utils.graph_wrapper.file_system import save_graph_as_json
from graph_utils.graph_wrapper.operation import simple_operation


class Graph_Wrapper:
    def __init__(self, nodes: list[Node]) -> None:
        self._data = Data(nodes)
        self._name = graph_const.DEFAULT_NAME
        self.hull_edges = []

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._data.name = name
        self._name = name

    def get_aktive_graph(self) -> "Data_Raw":
        return self._data.get_aktive_graph()

    def add_node(self, key: str, pos: tuple[int, int], degree: int) -> None:
        self._data.add_node(key, pos, degree)

    def check_for_intersection_except_corners(
        self,
        line1: shapely.geometry.LineString | tuple[str, str],
        line2: shapely.geometry.LineString | tuple[str, str],
    ) -> bool:
        return check.check_for_intersection_except_corners(self._data, line1, line2)

    def check_for_intersection_with_all_edges_and_nodes(
        self,
        edge: Union[tuple[str, str], shapely.LineString],
        check_if_active: bool = True,
    ) -> bool:
        return check.check_for_intersection_with_all_edges_and_nodes(
            self._data, edge, check_if_active
        )

    def show_and_save(self, show: bool = True, save: bool = True) -> None:
        visualisation.show_and_save(
            self._data,
            self._data.number_edges_in_Triangulation,
            show=show,
            save=save,
        )

    def add_edge(self, node1: str, node2: str, active: bool = True) -> None:
        """Fügt eine Kante zwischen zwei Knoten hinzu."""
        self._data.add_edge(node1, node2, active)

    def remove_edge(self, edge: tuple[str, str]) -> None:
        """Entfernt eine Kante zwischen zwei Knoten."""
        self._data.remove_edge(edge)

    def active_edge(
        self, node1: Union[str, Tuple[str, str]], node2: Optional[str] = None
    ) -> None:
        """Aktiviert eine Kante zwischen zwei Knoten."""
        self._data.active_edge(node1, node2)

    def deactivate_edge(
        self, node1: Union[str, Tuple[str, str]], node2: Optional[str] = None
    ) -> None:
        """Deaktiviert eine Kante zwischen zwei Knoten."""
        self._data.deactivate_edge(node1, node2)

    def is_edge_active(self, edge: tuple[str, str]) -> bool:
        """Überprüft, ob eine Kante aktiv ist."""
        return self._data.is_edge_active(edge)

    def add_all_possible_edges(self, default_for_active: bool = False) -> None:
        """Fügt alle möglichen Kanten zwischen den Knoten hinzu."""
        simple_operation.add_all_possible_edges(self._data, default_for_active)

    def get_all_edges(self, test_active: bool = False) -> list[tuple[str, str]]:
        """Gibt alle Kanten des Graphen zurück."""
        return self._data.get_all_edges(test_active)

    def get_hull_points(self) -> list[shapely.Point]:
        return self._data.get_hull_points()

    def get_hull_nodes(self) -> list[str]:
        return self._data.get_hull_nodes()

    def get_hull_edges(self) -> list[tuple[str, str]]:
        if self.hull_edges == []:
            self.hull_edges = self._data.get_hull_edges()
        return self.hull_edges

    def add_convex_hull(self) -> None:
        """Fügt den konvexen Rumpf der Punkte als Kante hinzu."""
        for edge in self.get_hull_edges():
            self.add_edge(edge[0], edge[1], True)

    def get_triangles_for_node(self, node: str) -> list[str]:
        """Gibt die Dreiecke des Graphen zurück."""
        return self._data.get_triangles_for_node(node)

    def get_triangles_for_edge(
        self, edge: tuple[str, str]
    ) -> list[tuple[str, str, str]]:
        """Gibt die Dreiecke des Graphen zurück."""
        return self._data.get_triangles_for_edge(edge)

    def get_all_triangles(self) -> list[tuple[str, str, str]]:
        """Gibt alle Dreiecke des Graphen zurück."""
        return self._data.get_all_triangles()

    def flip_edge(self, edge: tuple[str, str]) -> bool:
        return flip_edge.flip_edge(self._data, edge)

    def move_node(self, node: str = "", distance: int = -1) -> bool:
        return move_node.move_node(self._data, node, distance)

    def is_edge_in_graph(self, edge: tuple[str, str]) -> tuple[str, str]:
        return self._data.is_edge_in_graph(edge)

    def check_if_triangulation_with_degree_constraint(
        self, check_degree: bool = True, check_triangulation: bool = True
    ) -> bool:
        """Überprüft, ob der Graph eine Triangulation ist."""
        return check.check_if_triangulation_with_degree_constraint(
            self._data, check_degree, check_triangulation
        )

    def get_aktive_graph_nodes(self) -> list[Node]:
        return self._data.get_aktive_graph_nodes()

    def save_graph_as_json(self, filename: str = graph_const.DEFAULT_FILE_NAME) -> None:
        """Speichert den Graphen als JSON-Datei."""
        save_graph_as_json(self._data, filename)

    def get_all_nodes_name(self) -> list[str]:
        """Gibt alle Knoten des Graphen zurück."""
        return self._data.get_all_nodes_name()

    def get_number_edges_in_Triangulation(self) -> int:
        """Gibt die Anzahl der Kanten im Graphen zurück."""
        return self._data.number_edges_in_Triangulation

    def get_node_from_point(self, point: shapely.Point) -> str:
        return self._data.get_node_from_point(point)

    def check_node_for_degree(self, node: str) -> bool:
        """Überprüft, ob der Knoten die richtige Anzahl an Nachbarn hat."""
        return check.check_node_for_degree(self._data, node)

    def get_edges_for_node(self, node: str) -> list[tuple[str, str]]:
        """Gibt die Kanten des Graphen zurück."""
        return self._data.get_edges_for_node(node)

    def check_edge_interection_with_nodes(
        self,
        edge: Union[tuple[str, str], shapely.LineString],
        check_if_active: bool = True,
    ) -> bool:
        return check.check_edge_intersection_with_nodes(
            self._data, edge, check_if_active
        )

    def clear_all_edges(self) -> None:
        """Entfernt alle Kanten des Graphen."""
        self._data.clear_edges()

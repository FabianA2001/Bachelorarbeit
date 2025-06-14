from graph_utils import graph_const
from functools import cached_property
from graph_utils.node import Node
import shapely
from typing import Tuple, Union, Optional
from graph_utils.graph_wrapper.data import Data
from graph_utils.graph_wrapper.data_raw import Data_Raw
from graph_utils.graph_wrapper.check import Check
from graph_utils.graph_wrapper import visualisation
from graph_utils.graph_wrapper.operation import flip_edge
from graph_utils.graph_wrapper.operation import move_node
from graph_utils.graph_wrapper.operation.exclude_edge_partition import (
    Exclude_Edge_Partition,
)
from graph_utils.graph_wrapper.file_system import save_graph_as_json
import itertools
import logging


class Graph_Wrapper:
    def __init__(self, nodes: list[Node]) -> None:
        self._data = Data(nodes)
        self._name = graph_const.DEFAULT_NAME
        self._check = Check(self._data)
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

    def add_node(self, pos: tuple[int, int], degree: int) -> None:
        self.clear_cache()
        self._data.add_node(pos, degree)

    def check_for_intersection_except_corners(
        self,
        line1: shapely.geometry.LineString | tuple[int, int],
        line2: shapely.geometry.LineString | tuple[int, int],
    ) -> bool:
        return self._check.check_for_intersection_except_corners(line1, line2)

    def check_for_intersection_with_all_edges_and_nodes(
        self,
        edge: Union[tuple[int, int], shapely.LineString],
        check_if_active: bool = True,
    ) -> bool:
        return self._check.check_for_intersection_with_all_edges_and_nodes(
            edge, check_if_active
        )

    def get_intersections_with_all_edges_n2(
        self,
        edge: Union[tuple[int, int], shapely.LineString],
        check_if_active: bool = True,
    ) -> list[tuple[int, int]]:
        return self._check.get_intersections_with_all_edges_n2(edge, check_if_active)

    def get_intersections_with_all_edges(
        self,
        edge: tuple[int, int],
    ) -> list[tuple[int, int]]:
        return self._check.get_intersections_with_all_edges(edge)

    def get_all_intersections(
        self, timeout_func=lambda: ...
    ) -> set[tuple[tuple[int, int], tuple[int, int]]]:
        return self._check.get_all_intersections(timeout_func)

    def get_all_intersections_n2(
        self, check_if_active: bool = True, timeout_func=lambda: ...
    ) -> set[tuple[tuple[int, int], tuple[int, int]]]:
        return self._check.get_all_intersections_n2(check_if_active, timeout_func)

    def show_and_save(
        self, show: bool = True, save: bool = True, block: bool = False
    ) -> None:
        visualisation.show_and_save(
            self._data,
            self._check,
            self._data.get_number_edges_triangulation,
            show=show,
            save=save,
            block=block,
        )

    def add_edge(self, node1: int, node2: int, active: bool = True) -> None:
        """Fügt eine Kante zwischen zwei Knoten hinzu."""
        self.clear_cache()
        self._data.add_edge(node1, node2, active)

    def remove_edge(self, edge: tuple[int, int]) -> None:
        """Entfernt eine Kante zwischen zwei Knoten."""
        self.clear_cache()
        self._data.remove_edge(edge)

    def activate_edge(
        self, node1: Union[int, Tuple[int, int]], node2: Optional[int] = None
    ) -> None:
        """Aktiviert eine Kante zwischen zwei Knoten."""
        self.clear_cache()
        self._data.active_edge(node1, node2)

    def deactivate_edge(
        self, node1: Union[int, Tuple[int, int]], node2: Optional[int] = None
    ) -> None:
        """Deaktiviert eine Kante zwischen zwei Knoten."""
        self.clear_cache()
        self._data.deactivate_edge(node1, node2)

    def is_edge_active(self, edge: tuple[int, int]) -> bool:
        """Überprüft, ob eine Kante aktiv ist."""
        return self._data.is_edge_active(edge)

    def get_all_edges(self, test_active: bool = False) -> list[tuple[int, int]]:
        """Gibt alle Kanten des Graphen zurück."""
        if test_active:
            return self._data.all_edges_aktive
        else:
            return self._data.all_edges

    def get_hull_points(self) -> list[shapely.Point]:
        return self._data.get_hull_points

    def get_hull_nodes(self) -> list[int]:
        return self._data.get_hull_nodes

    def get_hull_edges(self) -> list[tuple[int, int]]:
        if self.hull_edges == []:
            self.hull_edges = self._data.get_hull_edges
        return self.hull_edges

    def add_convex_hull(self) -> None:
        """Fügt den konvexen Rumpf der Punkte als Kante hinzu."""
        self.clear_cache()
        for edge in self.get_hull_edges():
            self.add_edge(edge[0], edge[1], True)

    def get_triangles_for_node(self, node: int) -> list[int]:
        """Gibt die Dreiecke des Graphen zurück."""
        return self._data.get_triangles_for_node(node)

    def get_triangles_for_edge(
        self, edge: tuple[int, int]
    ) -> list[tuple[int, int, int]]:
        """Gibt die Dreiecke des Graphen zurück."""
        return self._data.get_triangles_for_edge(edge)

    def get_all_triangles(self) -> list[tuple[int, int, int]]:
        """Gibt alle Dreiecke des Graphen zurück."""
        return self._data.get_all_triangles

    def flip_edge(self, edge: tuple[int, int]) -> bool:
        self.clear_cache()
        return flip_edge.flip_edge(self._data, self._check, edge)

    def move_node(self, node: int = 0, distance: int = -1) -> bool:
        self.clear_cache()
        return move_node.move_node(self._data, node, distance)

    def is_edge_in_graph(self, edge: tuple[int, int]) -> tuple[int, int]:
        return self._data.is_edge_in_graph(edge)

    def check_if_triangulation_with_degree_constrained(
        self, check_degree: bool = True, check_triangulation: bool = True
    ) -> bool:
        """Überprüft, ob der Graph eine Triangulation ist."""
        return self._check.check_if_triangulation_with_degree_constraint(
            check_degree, check_triangulation
        )

    def get_aktive_graph_nodes(self) -> list[Node]:
        return self._data.get_aktive_graph_nodes

    def save_graph_as_json(self, filename: str = graph_const.DEFAULT_FILE_NAME) -> None:
        """Speichert den Graphen als JSON-Datei."""
        save_graph_as_json(self._data, filename)

    def get_all_nodes_name(self) -> list[int]:
        """Gibt alle Knoten des Graphen zurück."""
        return self._data.get_all_nodes_name

    def get_number_edges_in_Triangulation(self) -> int:
        """Gibt die Anzahl der Kanten im Graphen zurück."""
        return self._data.get_number_edges_triangulation

    def get_number_tris_in_Triangulation(self) -> int:
        """Gibt die Anzahl der Dreiecke im Graphen zurück."""
        return self._data.get_number_tris_triangulation

    def get_node_from_point(self, point: shapely.Point) -> int:
        return self._data.get_node_from_point(point)

    def get_point_from_node(self, node: int) -> shapely.Point:
        """Gibt den Punkt des Knotens zurück."""
        return self._data.get_point_from_node(node)

    def get_pos_from_node(self, node: int) -> tuple[int, int]:
        """Gibt die Position des Knotens zurück."""
        return self._data.get_pos_from_node(node)

    def check_node_for_degree(self, node: int) -> bool:
        """Überprüft, ob der Knoten die richtige Anzahl an Nachbarn hat."""
        return self._check.check_node_for_degree(node)

    def get_edges_of_node(self, node: int) -> list[tuple[int, int]]:
        """Gibt die Kanten des Graphen zurück."""
        return self._data.get_edges_for_node(node)

    def check_edge_interection_with_nodes(
        self,
        edge: Union[tuple[int, int], shapely.LineString],
        check_if_active: bool = True,
    ) -> bool:
        return self._check.check_edge_intersection_with_nodes(edge, check_if_active)

    def clear_all_edges(self) -> None:
        """Entfernt alle Kanten des Graphen."""
        logging.info("Clearing all edges in the graph.")
        self.clear_cache()
        self._data.clear_edges()

    def number_of_correct_nodes(self) -> int:
        """Gibt die Anzahl der Knoten im Graphen zurück."""
        counter = 0
        for node in self.get_all_nodes_name():
            if self.check_node_for_degree(node):
                counter += 1
        return counter

    def percentage_of_correct_nodes(self) -> float:
        """Gibt den Prozentsatz der Knoten im Graphen zurück, die die richtige Anzahl an Nachbarn haben."""
        return self.number_of_correct_nodes() / len(self.get_all_nodes_name()) * 100

    def add_all_possible_edges(
        self, default_for_active: bool = False, ignore_hull: bool = False
    ) -> None:
        self.clear_cache()
        """Fügt alle möglichen Kanten zwischen den Knoten hinzu."""
        hull = self.get_hull_edges()
        combinations = list(itertools.combinations(self._data.nodes, 2))
        for com in combinations:
            self._data.add_edge(com[0], com[1], default_for_active)
            if self._check.check_edge_intersection_with_nodes(com, False):
                self._data.remove_edge(com)
            if ((com in hull) or ((com[1], com[0]) in hull)) and ignore_hull:
                self._data.remove_edge(com)

    def get_desired_degree_node(self, node: int) -> int:
        """Gibt den Grad eines Knotens zurück."""
        if node not in self._data.nodes:
            raise ValueError(f"Node {node} does not exist in the graph.")
        return self._data.nodes[node].get("degree")

    def get_degree_of_node(self, node: int) -> int:
        """Gibt den Grad eines Knotens zurück."""
        if node not in self.get_all_nodes_name():
            raise ValueError(f"Node {node} does not exist in the graph.")
        return self._data.degree(node)

    def evaluate_graph(self) -> float:
        evaluation = 0.0
        number_of_nodes = len(self.get_all_nodes_name())
        for node in self.get_all_nodes_name():
            desired_degree = self.get_desired_degree_node(node)
            degree = self._data.degree_aktive(node)
            x = (
                desired_degree - min(abs(desired_degree - degree), desired_degree)
            ) / desired_degree
            evaluation += x

        evaluation /= number_of_nodes

        assert (
            evaluation >= 0
        ), f"Evaluation must be non-negative, but got {evaluation}."
        assert (
            evaluation <= 1
        ), f"Evaluation must be smaller then 1, but got {evaluation}."
        return evaluation

    def exclude_edge_partition(self) -> list[tuple[int, int]]:
        return Exclude_Edge_Partition(self._data)()

    def check_degree_possible(self) -> bool:
        """Überprüft, ob der Graph eine Triangulation ist und ob die Knotengrade möglich sind."""
        return self._check.check_degree_possible()

    def clear_cache(self) -> None:
        """Leert alle gecachten Properties (cached_property) dieser Instanz."""
        for cls in self.__class__.__mro__:
            for name, attr in cls.__dict__.items():
                if isinstance(attr, cached_property):
                    self.__dict__.pop(name, None)

    @cached_property
    def impossible_edges(self) -> list[tuple[int, int]]:
        """Gibt alle Kanten zurück, die nicht im Graphen vorhanden sind."""
        impossible_edges = []
        for node1, node2 in itertools.combinations(self.get_all_nodes_name(), 2):
            if self.check_edge_interection_with_nodes((node1, node2), False):
                impossible_edges.append((min(node1, node2), max(node1, node2)))
        return impossible_edges

    @cached_property
    def get_max_degree(self) -> int:
        """Gibt den maximalen Grad des Graphen zurück."""
        return max(
            self.get_desired_degree_node(node) for node in self.get_all_nodes_name()
        )

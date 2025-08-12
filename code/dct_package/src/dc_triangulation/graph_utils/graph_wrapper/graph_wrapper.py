import itertools
import logging
from functools import cached_property
from typing import Optional, Tuple, Union

import networkx as nx
import shapely

from ...cpp._cpp_bindings import intersection as intersection_cpp_extern
from ...cpp._cpp_bindings import max_clique, triangles_intersection
from .. import graph_const
from ..node import Node
from . import visualisation
from .check import Check
from .data import Data
from .data_raw import Data_Raw
from .file_system import save_graph_as_json
from .operation import flip_edge, move_node
from .operation.exclude_edge_intersection import Exclude_Edge_Intersection
from .operation.exclude_edge_partition import Exclude_Edge_Partition


class Graph_Wrapper:
    def __init__(self, nodes: list[Node]) -> None:
        self._data = Data(nodes)
        self._name = graph_const.DEFAULT_NAME
        self._check = Check(self._data)

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

    # Testet nicht für impossible edges
    def get_all_intersections(
        self, timeout_func=lambda: ...
    ) -> dict[tuple[int, int], list[tuple[int, int]]]:
        return self._check.get_all_intersections(timeout_func)

    def get_all_intersections_n2(
        self, check_if_active: bool = True, timeout_func=lambda: ...
    ) -> dict[tuple[int, int], set[tuple[int, int]]]:
        return self._check.get_all_intersections_n2(check_if_active, timeout_func)

    def get_all_intersections_cpp(
        self, timeout_func=lambda: ...
    ) -> dict[tuple[int, int], set[tuple[int, int]]]:
        x = self.__get_all_intersections_cpp_cached
        timeout_func()
        return x

    def get_all_triangles_intersections_cpp(
        self,
    ) -> dict[tuple[int, int, int], set[tuple[int, int, int]]]:
        """Gibt alle Dreiecksintersektionen zurück."""
        triangles = self.get_all_triangles()
        triangles_pos = [
            [self.get_pos_from_node(node) for node in triangle]
            for triangle in triangles
        ]
        # print(str(triangles).replace(")", "}").replace("(", "{"))
        # print(
        #     str(
        #         [
        #             str(pos)
        #             .replace(")", "}")
        #             .replace("(", "{")
        #             .replace("]", "}")
        #             .replace("[", "{")
        #             for pos in triangles_pos
        #         ]
        #     )
        #     .replace(")", "}")
        #     .replace("(", "{")
        #     .replace("]", "}")
        #     .replace("[", "{")
        #     .replace("'", "")
        # )
        return triangles_intersection(triangles, triangles_pos)

    def show_and_save(
        self,
        show: bool = True,
        save: str = "",
        block: bool = True,
        show_set_false: bool = False,
    ) -> None:
        if not show_set_false:
            visualisation.draw(
                self._data,
                self._check,
                self._data.get_number_edges_triangulation,
                show=show,
                save=save,
                block=block,
            )
        else:
            visualisation.draw_with_set_false(
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

    def edge_show_false(
        self, node1: Union[int, Tuple[int, int]], node2: Optional[int] = None
    ) -> None:
        """Setzt eine Kante auf 'show_false'."""
        self._data.edge_show_false(node1, node2)

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
        return self._data.get_hull_edges

    def add_convex_hull(self) -> None:
        """Fügt den konvexen Rumpf der Punkte als Kante hinzu."""
        self.clear_cache()
        for edge in self.get_hull_edges():
            self.add_edge(edge[0], edge[1], True)

    def get_triangles_from_node(self, node: int) -> list[int]:
        """Gibt die Dreiecke des Graphen zurück."""
        return self._data.get_empty_triangles_for_node(node)

    def get_triangles_for_edge(
        self, edge: tuple[int, int]
    ) -> list[tuple[int, int, int]]:
        """Gibt die Dreiecke des Graphen zurück."""
        return self._data.get_triangles_for_edge(edge)

    def get_all_triangles(self) -> list[tuple[int, int, int]]:
        """Gibt alle Dreiecke des Graphen zurück."""
        assert len(self._data.edges) >= 3, (
            "Graph must have at least 3 edges to form triangles."
        )
        return self._data.get_all_empty_triangles

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

    def save_graph_as_json(
        self, path: str, filename: str = graph_const.DEFAULT_FILE_NAME
    ) -> None:
        """Speichert den Graphen als JSON-Datei."""
        save_graph_as_json(self._data, path, filename)

    def get_all_nodes(self) -> list[int]:
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

    def deactivate_all_edges(self) -> None:
        """Deaktiviert alle Kanten des Graphen."""
        logging.info("Deactivating all edges in the graph.")
        self.clear_cache()
        for edge in self._data.get_all_edges():
            self._data.deactivate_edge(edge)

    def number_of_correct_nodes(self) -> int:
        """Gibt die Anzahl der Knoten im Graphen zurück."""
        counter = 0
        for node in self.get_all_nodes():
            if self.check_node_for_degree(node):
                counter += 1
        return counter

    def percentage_of_correct_nodes(self) -> float:
        """Gibt den Prozentsatz der Knoten im Graphen zurück, die die richtige Anzahl an Nachbarn haben."""
        return self.number_of_correct_nodes() / len(self.get_all_nodes()) * 100

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

    def get_line_of_edge(self, edge: tuple[int, int]) -> shapely.LineString:
        """Gibt die Linie einer Kante zurück."""
        return self._data.get_line_of_edge(edge)

    def get_desired_degree_node(self, node: int) -> int:
        """Gibt den Grad eines Knotens zurück."""
        if node not in self._data.nodes:
            raise ValueError(f"Node {node} does not exist in the graph.")
        return self._data.nodes[node].get("degree")

    def get_degree_of_node(self, node: int) -> int:
        """Gibt den Grad eines Knotens zurück."""
        if node not in self.get_all_nodes():
            raise ValueError(f"Node {node} does not exist in the graph.")
        return self._data.degree(node)

    def evaluate(self) -> float:
        evaluation = 0.0
        number_of_nodes = len(self.get_all_nodes())
        for node in self.get_all_nodes():
            desired_degree = self.get_desired_degree_node(node)
            degree = self._data.degree_aktive(node)
            x = (
                desired_degree - min(abs(desired_degree - degree), desired_degree)
            ) / desired_degree
            evaluation += x

        evaluation /= number_of_nodes

        assert evaluation >= 0, (
            f"Evaluation must be non-negative, but got {evaluation}."
        )
        assert evaluation <= 1, (
            f"Evaluation must be smaller then 1, but got {evaluation}."
        )
        return evaluation

    def check_degree_possible(self) -> str:
        """Überprüft, ob der Graph eine Triangulation ist und ob die Knotengrade möglich sind."""
        return self._check.check_degree_possible()

    def clear_cache(self) -> None:
        """Leert alle gecachten Properties (cached_property) dieser Instanz."""
        for cls in self.__class__.__mro__:
            for name, attr in cls.__dict__.items():
                if isinstance(attr, cached_property):
                    self.__dict__.pop(name, None)

    def get_all_active_edges(self) -> list[tuple[int, int]]:
        """Gibt alle aktiven Kanten des Graphen zurück."""
        return self._data.get_all_active_edges

    @cached_property
    def impossible_edges(self) -> list[tuple[int, int]]:
        """Gibt alle Kanten zurück, die nicht im Graphen vorhanden sind."""
        impossible_edges = []
        for node1, node2 in itertools.combinations(self.get_all_nodes(), 2):
            if self.check_edge_interection_with_nodes((node1, node2), False):
                impossible_edges.append((min(node1, node2), max(node1, node2)))
        return impossible_edges

    @cached_property
    def get_max_degree(self) -> int:
        """Gibt den maximalen Grad des Graphen zurück."""
        return max(self.get_desired_degree_node(node) for node in self.get_all_nodes())

    @cached_property
    def exclude_edges(self) -> list[tuple[int, int]]:
        edges = Exclude_Edge_Partition(self._data, self.impossible_edges)()
        edges.extend(
            Exclude_Edge_Intersection(self._data, self.get_all_intersections_cpp())()
        )
        return [edge for edge in edges if edge not in self.impossible_edges]

    @cached_property
    def __get_all_intersections_cpp_cached(
        self,
    ) -> dict[tuple[int, int], set[tuple[int, int]]]:
        poss = [self.get_pos_from_node(edge) for edge in self.get_all_nodes()]
        return intersection_cpp_extern(
            self.get_all_nodes(), poss, self.impossible_edges
        )

    @cached_property
    def get_intersection_clique(self) -> list[list[tuple[int, int]]]:
        edge_dict = self.get_all_intersections_cpp()
        edge_graph = nx.Graph()
        for edge, neighbors in edge_dict.items():
            for neighbor in neighbors:
                edge_graph.add_edge(edge, neighbor)

        return list(nx.find_cliques(edge_graph))

    @cached_property
    def get_intersection_clique_cpp(self) -> list[set[tuple[int, int]]]:
        edge_dict = self.get_all_intersections_cpp()
        return max_clique(edge_dict)

    @cached_property
    def fix_edges(self) -> set[tuple[int, int]]:
        """Gibt die Kanten zurück, die fixiert werden sollen."""
        edges = set()
        hull_nodes = self.get_hull_nodes()
        for node1, node2, node3 in zip(
            hull_nodes,
            hull_nodes[1:] + hull_nodes[:-1],
            hull_nodes[2:] + hull_nodes[:-2],
        ):
            if self.get_desired_degree_node(node2) != 2:
                edges.add((min(node1, node3), max(node1, node3)))
        return edges

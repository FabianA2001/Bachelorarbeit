import networkx as nx
import matplotlib.pyplot as plt
from graph_utils import graph_const
from graph_utils.node import Node, save_nodes_as_json
import shapely
import itertools
from typing import Tuple, Union, Optional
import logging
import math
import random
from graph_utils.graph_wrapper.data import Data
from graph_utils.graph_wrapper import check


def flip_edge(data: Data, edge: tuple[str, str]) -> bool:
    def reduce_to_two_tri(
        triangles: list[tuple[str, str, str]],
    ) -> list[tuple[str, str, str]]:
        """Reduziert die Liste der Dreiecke auf zwei."""
        nodes = set()
        for tri in triangles:
            for node in tri:
                if node != edge[0] and node != edge[1]:
                    nodes.add(node)
        points = [data.nodes[node].get("point") for node in nodes]

        # logging.warning("starte While Schleife")
        counter = 0
        while len(triangles) > 2:
            counter += 1
            if counter > 500:
                raise ValueError(
                    "Zu viele Iterationen in reduce_to_two_tri.")
            for tri in triangles:
                tri_points = [data.nodes[node].get(
                    "point") for node in tri]
                poly = shapely.geometry.Polygon(tri_points)
                if not poly.is_valid:
                    raise ValueError(
                        f"Polygon {poly} is not valid.\n{tri_points}")
                for node, point in zip(nodes, points):
                    if node in tri:
                        continue
                    if poly.contains(point):
                        triangles.remove(tri)
                        break
        return triangles

    """Flippt eine Kante im Graphen."""
    edge = data.is_edge_in_graph(edge)
    triangles = data.get_triangles_for_edge(edge)
    if len(triangles) <= 1:
        return False

    if len(triangles) > 2:
        triangles = reduce_to_two_tri(triangles)
    assert len(
        triangles) == 2, f"Edge {edge} is not a diagonal.\n{triangles}"

    triangle1, triangle2 = triangles
    for node in triangle1:
        if edge[0] != node and edge[1] != node:
            a = node
    for node in triangle2:
        if edge[0] != node and edge[1] != node:
            b = node
    edges = data.get_all_edges()
    if (a, b) in edges or (b, a) in edges:
        return False

    data.add_edge(a, b, True)
    data.deactivate_edge(edge)
    if check.check_for_intersection_with_all_edges_and_nodes(data, (a, b), True):
        data.remove_edge((a, b))
        data.active_edge(edge)
        # logging.warning(
        #     f"({a},{b}) würde mit einer anderen Kante schneiden.")
        return False
    # logging.info(
    #     f"({a},{b}) wurde erfolgreich hinzugefügt und ({edge[0]},{edge[1]}) entfernt.")
    data.remove_edge(edge)
    return True

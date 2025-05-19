import shapely
from typing import Union
from graph_utils.graph_wrapper.data import Data


def check_for_intersection_except_corners(
    data: Data,
    line1: shapely.geometry.LineString | tuple[str, str],
    line2: shapely.geometry.LineString | tuple[str, str],
) -> bool:
    if isinstance(line1, tuple):
        line1 = data.edges[line1].get("line")
    if isinstance(line2, tuple):
        line2 = data.edges[line2].get("line")

    corner_points = [data.nodes[node].get("point") for node in data.nodes]
    intersection = line1.intersection(line2)  # type: ignore
    if intersection.is_empty:
        return False
    # Überprüfen, ob der Schnittpunkt einer der Eckpunkte ist
    if isinstance(intersection, shapely.geometry.Point):
        return intersection not in corner_points
    else:
        return True


def check_for_intersection_with_all_edges_and_nodes(
    data: Data,
    edge: Union[tuple[str, str], shapely.LineString],
    check_if_active: bool = True,
) -> bool:
    """Überprüft, ob eine Linie mit einer anderen Linie im Graphen schneidet."""
    if isinstance(edge, tuple):
        if check_if_active:
            if not data.edges[edge].get("active"):
                return False
        line = data.edges[edge].get("line")
    elif isinstance(edge, shapely.LineString):
        line = edge
    else:
        raise ValueError("Erwarte Tuple oder LineString")

    points = [data.nodes[node].get("point") for node in data.nodes]
    multipoint = shapely.geometry.MultiPoint(points)
    intersection = multipoint.intersection(line)
    if not isinstance(intersection, shapely.geometry.MultiPoint):
        raise ValueError(f"Intersection is not a MultiPoint, but {type(intersection)}")
    if len(intersection.geoms) > 2:
        return True

    # Überprüfen, ob die Linie mit einer anderen Linie im Graphen schneidet
    all_linestrings_from_edges = [
        data.edges[edge].get("line")
        for edge in data.edges
        if data.edges[edge].get("active") or not check_if_active
    ]
    for other in all_linestrings_from_edges:
        if line == other:
            continue
        if check_for_intersection_except_corners(data, line, other):
            return True

    return False


def check_if_triangulation_with_degree_constraint(data: Data) -> bool:
    """Überprüft, ob der Graph eine Triangulation ist."""
    lokal_graph = data.get_aktive_graph()
    edges = lokal_graph.get_all_edges()
    if len(edges) != data.number_edges_in_Triangulation:
        return False
    for edge in edges:
        if check_for_intersection_with_all_edges_and_nodes(data, edge):
            return False
    for node in data.get_all_nodes_name():
        if lokal_graph.nodes[node].get("degree") != lokal_graph.degree(node):
            return False
    return True

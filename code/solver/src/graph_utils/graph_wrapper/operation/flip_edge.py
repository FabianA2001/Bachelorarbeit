import shapely
from graph_utils.graph_wrapper.data import Data
from graph_utils.graph_wrapper.visualisation import show_and_save
from graph_utils.graph_wrapper.check import Check


def flip_edge(data: Data, check: Check, edge: tuple[int, int]) -> bool:
    if not isinstance(edge, tuple) or len(edge) != 2:
        raise ValueError(f"Erwarte Tuple aber erhalte {type(edge)}, {edge}")
        if not all(isinstance(x, int) for x in edge):
            raise ValueError(
                f"Erwarte Tuple mit Strings aber erhalte {type(edge)}, {edge}"
            )

    def reduce_to_two_tri(
        triangles: list[tuple[int, int, int]],
    ) -> list[tuple[int, int, int]]:
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
                show_and_save(
                    data,
                    check,
                    data.get_number_edges_triangulation,
                    show=True,
                    save=False,
                )

                raise ValueError("Zu viele Iterationen in reduce_to_two_tri.")
            for tri in triangles:
                tri_points = [data.nodes[node].get("point") for node in tri]
                poly = shapely.geometry.Polygon(tri_points)
                if not poly.is_valid:
                    raise ValueError(f"Polygon {poly} is not valid.\n{tri_points}")
                for node, point in zip(nodes, points):
                    if node in tri:
                        continue
                    if poly.contains(point):
                        triangles.remove(tri)
                        break
        return triangles

    """Flippt eine Kante im Graphen."""
    edge = data.is_edge_in_graph(edge)
    if data.check_if_edge_in_hull(edge):
        return False

    triangles = data.get_triangles_for_edge(edge)
    if len(triangles) <= 1:
        return False

    if len(triangles) > 2:
        triangles = reduce_to_two_tri(triangles)
    if len(triangles) != 2:
        show_and_save(
            data,
            check,
            data.get_number_edges_triangulation,
            show=True,
            save=False,
        )

    assert len(triangles) == 2, f"Edge {edge} is not a diagonal.\n{triangles}"

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
    if check.check_for_intersection_with_all_edges_and_nodes((a, b), True):
        data.remove_edge((a, b))
        data.active_edge(edge)
        # logging.warning(
        #     f"({a},{b}) würde mit einer anderen Kante schneiden.")
        return False
    # logging.info(
    #     f"Flippe Kante {edge} zu ({a},{b})")
    data.remove_edge(edge)
    return True

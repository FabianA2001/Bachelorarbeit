import os
from dataclasses import asdict

from dc_triangulation import (
    SAT,
    Graph_Wrapper,
    Node,
    SAT_Parameter,
    load_nodes_from_json,
)


def test_add_convex_hull():
    nodes = [
        Node((0, 0)),
        Node((0, 1)),
        Node((1, 0)),
        Node((1, 1)),
    ]
    graph = Graph_Wrapper(nodes)
    graph.add_convex_hull()
    assert len(graph.get_all_edges()) == 4
    all_edges = graph.get_all_edges()
    assert (0, 1) in all_edges
    assert (0, 2) in all_edges
    assert (1, 3) in all_edges
    assert (2, 3) in all_edges


def test_flip():
    # Test the flip function
    nodes = [
        Node((0, 0)),
        Node((0, 1)),
        Node((1, 0)),
        Node((1, 1)),
    ]
    graph = Graph_Wrapper(nodes)
    graph.add_convex_hull()
    graph.add_edge(0, 3)
    assert graph.flip_edge((0, 3))
    assert (1, 2) in graph.get_all_edges()
    assert not graph.flip_edge((0, 1))


def test_check_for_intersection_except_corners():
    # Test the check_for_intersection_except_corners function
    nodes = [
        Node((0, 0)),
        Node((0, 1)),
        Node((1, 0)),
        Node((1, 1)),
    ]
    graph = Graph_Wrapper(nodes)
    graph.add_convex_hull()
    graph.add_edge(0, 3)
    graph.add_edge(1, 2)
    assert graph.check_for_intersection_except_corners((0, 3), (1, 2))
    assert not graph.check_for_intersection_except_corners((0, 3), (0, 1))


def test_add_all_possible_edges():
    # Test the add_all_possible_edges function
    nodes = [
        Node((0, 0)),
        Node((0, 1)),
        Node((1, 0)),
        Node((1, 1)),
    ]
    graph = Graph_Wrapper(nodes)
    graph.add_all_possible_edges()
    assert len(graph.get_all_edges()) == 6
    all_edges = graph.get_all_edges()
    assert (0, 1) in all_edges
    assert (0, 2) in all_edges
    assert (0, 3) in all_edges
    assert (1, 2) in all_edges
    assert (1, 3) in all_edges
    assert (2, 3) in all_edges


def test_get_triangles_for_node():
    # Test the get_triangles_for_node function
    nodes = [
        Node((0, 0)),
        Node((0, 1)),
        Node((1, 0)),
        Node((1, 1)),
    ]
    graph = Graph_Wrapper(nodes)
    graph.add_convex_hull()
    graph.add_edge(0, 3)
    triangles = graph.get_triangles_from_node(0)
    assert len(triangles) == 2
    assert (0, 1, 3) in triangles
    assert (0, 2, 3) in triangles


def test_get_triangles_for_edge():
    # Test the get_triangles_for_node function
    nodes = [
        Node((0, 0)),
        Node((0, 1)),
        Node((1, 0)),
        Node((1, 1)),
    ]
    graph = Graph_Wrapper(nodes)
    graph.add_convex_hull()
    graph.add_edge(0, 3)
    triangles = graph.get_triangles_for_edge((0, 3))
    assert len(triangles) == 2
    assert (0, 1, 3) in triangles
    assert (0, 2, 3) in triangles


def test_get_hull_nodes():
    # Test the get_hull_nodes function
    nodes = [
        Node((5, 10)),
        Node((2, 6)),
        Node((6, 5)),
        Node((9, 3)),
        Node((0, 10)),
        Node((9, 5)),
        Node((1, 2)),
        Node((8, 6)),
        Node((2, 3)),
        Node((2, 10)),
    ]
    graph = Graph_Wrapper(nodes)
    hull = graph.get_hull_nodes()
    assert 4 in hull
    assert 9 in hull
    assert 0 in hull
    assert 5 in hull
    assert 3 in hull
    assert 6 in hull
    assert len(hull) == 6


def test_get_hull_edges():
    # Test the get_hull_edges function
    nodes = [
        Node((5, 10)),
        Node((2, 6)),
        Node((6, 5)),
        Node((9, 3)),
        Node((0, 10)),
        Node((9, 5)),
        Node((1, 2)),
        Node((8, 6)),
        Node((2, 3)),
        Node((2, 10)),
    ]
    graph = Graph_Wrapper(nodes)
    hull = graph.get_hull_edges()
    assert (4, 9) in hull
    assert (0, 9) in hull
    assert (0, 5) in hull
    assert (3, 5) in hull
    assert (3, 6) in hull
    assert (4, 6) in hull
    assert len(hull) == 6


def test_check_if_triangulation_with_degree_constraint():
    nodes = [
        Node((0, 0), 3),
        Node((0, 1), 2),
        Node((1, 0), 2),
        Node((1, 1), 3),
    ]
    graph = Graph_Wrapper(nodes)
    assert not graph.check_if_triangulation_with_degree_constrained()
    graph.add_edge(0, 1)
    graph.add_edge(0, 2)
    graph.add_edge(3, 1)
    graph.add_edge(3, 2)
    assert not graph.check_if_triangulation_with_degree_constrained()
    graph.add_edge(0, 3)
    graph.add_edge(1, 2)
    assert not graph.check_if_triangulation_with_degree_constrained()
    graph.deactivate_edge(1, 2)
    assert graph.check_if_triangulation_with_degree_constrained()
    graph.remove_edge((1, 3))
    assert not graph.check_if_triangulation_with_degree_constrained()


def test_activate_edge():
    # Test the activate_edge function
    nodes = [
        Node((0, 0)),
        Node((0, 1)),
        Node((1, 0)),
        Node((1, 1)),
    ]
    graph = Graph_Wrapper(nodes)
    graph.add_edge(0, 3)
    assert (0, 3) in graph.get_all_edges(True)
    graph.deactivate_edge(0, 3)
    assert (0, 3) not in graph.get_all_edges(True)
    graph.activate_edge(0, 3)
    assert (0, 3) in graph.get_all_edges(True)


def test_check_for_intersection_with_all_edges_and_nodes():
    # Test the check_for_intersection_with_all_edges_and_nodes function
    nodes = [
        Node((0, 0)),
        Node((0, 1)),
        Node((1, 0)),
        Node((1, 1)),
    ]
    graph = Graph_Wrapper(nodes)
    graph.add_convex_hull()
    graph.add_edge(0, 3)
    graph.add_edge(1, 2)
    assert graph.check_for_intersection_with_all_edges_and_nodes((0, 3))
    assert not graph.check_for_intersection_with_all_edges_and_nodes((0, 1))


def test_get_intersections_with_all_edges():
    nodes = [
        Node((5, 10)),
        Node((2, 6)),
        Node((6, 5)),
        Node((9, 3)),
        Node((0, 10)),
        Node((9, 5)),
        Node((1, 2)),
        Node((8, 6)),
        Node((2, 3)),
        Node((2, 10)),
    ]
    graph = Graph_Wrapper(nodes)
    graph.add_all_possible_edges(True)
    edge = (1, 3)
    assert graph.get_intersections_with_all_edges_n2(
        edge, False
    ) == graph.get_intersections_with_all_edges(edge)


def test_get_all_intersections():
    nodes = [
        Node((5, 10)),
        Node((2, 6)),
        Node((6, 5)),
        Node((9, 3)),
        Node((0, 10)),
        Node((9, 5)),
        Node((1, 2)),
        Node((8, 6)),
        Node((2, 3)),
        Node((2, 10)),
    ]
    graph = Graph_Wrapper(nodes)
    graph.add_all_possible_edges(True)
    intersections = graph.get_all_intersections_n2()
    for edge in [
        (edge, other)
        for edge, other in graph.get_all_intersections()
        if edge not in graph.impossible_edges and other not in graph.impossible_edges
    ]:
        assert edge in intersections


def test_exclude_edges():
    PATH = os.path.join(os.path.dirname(__file__), "instance", "10_delaunay_flips.json")
    # PATH = os.path.join(os.path.dirname(__file__), "instance", "50_delaunay_flips.json")
    # PATH = os.path.join(os.path.dirname(__file__), "instance", "80_random.json")
    nodes = load_nodes_from_json(PATH)
    outer_graph = Graph_Wrapper(nodes)
    outer_graph.add_convex_hull()
    outer_graph.add_edge(13, 29)
    # outer_graph.show_and_save(show=False, save=".")
    for edge in [
        edge
        for edge in outer_graph.exclude_edge_partition
        if edge not in outer_graph.impossible_edges
    ]:
        graph = Graph_Wrapper(nodes)
        solver = SAT(graph)
        para = SAT_Parameter(
            intersection=True,
            degree_atleast=True,
        )
        try:
            solver.solve(
                {"timeout": -1, "args": asdict(para), "debug_set_edges": [edge]}
            )
        except AssertionError:
            continue

        graph.show_and_save()
        assert False, f"Solver should not find a solution with excluded edge {edge}."


test_exclude_edges()

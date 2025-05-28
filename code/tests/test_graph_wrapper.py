from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from graph_utils.node import Node


def test_add_convex_hull():
    nodes = [
        Node("A", (0, 0)),
        Node("B", (0, 1)),
        Node("C", (1, 0)),
        Node("D", (1, 1)),
    ]
    graph = Graph_Wrapper(nodes)
    graph.add_convex_hull()
    assert len(graph.get_all_edges()) == 4
    all_edges = graph.get_all_edges()
    assert ("A", "B") in all_edges
    assert ("B", "D") in all_edges
    assert ("C", "D") in all_edges
    assert ("A", "C") in all_edges


def test_flip():
    # Test the flip function
    nodes = [
        Node("A", (0, 0)),
        Node("B", (0, 1)),
        Node("C", (1, 0)),
        Node("D", (1, 1)),
    ]
    graph = Graph_Wrapper(nodes)
    graph.add_convex_hull()
    graph.add_edge("A", "D")
    assert graph.flip_edge(("A", "D"))
    assert ("B", "C") in graph.get_all_edges()
    assert not graph.flip_edge(("A", "B"))


def test_check_for_intersection_except_corners():
    # Test the check_for_intersection_except_corners function
    nodes = [
        Node("A", (0, 0)),
        Node("B", (0, 1)),
        Node("C", (1, 0)),
        Node("D", (1, 1)),
    ]
    graph = Graph_Wrapper(nodes)
    graph.add_convex_hull()
    graph.add_edge("A", "D")
    graph.add_edge("B", "C")
    assert graph.check_for_intersection_except_corners(("A", "D"), ("B", "C"))
    assert not graph.check_for_intersection_except_corners(("A", "D"), ("A", "B"))


def test_add_all_possible_edges():
    # Test the add_all_possible_edges function
    nodes = [
        Node("A", (0, 0)),
        Node("B", (0, 1)),
        Node("C", (1, 0)),
        Node("D", (1, 1)),
    ]
    graph = Graph_Wrapper(nodes)
    graph.add_all_possible_edges()
    assert len(graph.get_all_edges()) == 6
    all_edges = graph.get_all_edges()
    assert ("A", "B") in all_edges
    assert ("A", "C") in all_edges
    assert ("A", "D") in all_edges
    assert ("B", "C") in all_edges
    assert ("B", "D") in all_edges
    assert ("C", "D") in all_edges


def test_get_triangles_for_node():
    # Test the get_triangles_for_node function
    nodes = [
        Node("A", (0, 0)),
        Node("B", (0, 1)),
        Node("C", (1, 0)),
        Node("D", (1, 1)),
    ]
    graph = Graph_Wrapper(nodes)
    graph.add_convex_hull()
    graph.add_edge("A", "D")
    triangles = graph.get_triangles_for_node("A")
    assert len(triangles) == 2
    assert ("A", "B", "D") in triangles
    assert ("A", "C", "D") in triangles


def test_get_triangles_for_edge():
    # Test the get_triangles_for_node function
    nodes = [
        Node("A", (0, 0)),
        Node("B", (0, 1)),
        Node("C", (1, 0)),
        Node("D", (1, 1)),
    ]
    graph = Graph_Wrapper(nodes)
    graph.add_convex_hull()
    graph.add_edge("A", "D")
    triangles = graph.get_triangles_for_edge(("A", "D"))
    assert len(triangles) == 2
    assert ("A", "B", "D") in triangles
    assert ("A", "C", "D") in triangles


def test_get_hull_nodes():
    # Test the get_hull_nodes function
    nodes = [
        Node("0", (5, 10)),
        Node("1", (2, 6)),
        Node("2", (6, 5)),
        Node("3", (9, 3)),
        Node("4", (0, 10)),
        Node("5", (9, 5)),
        Node("6", (1, 2)),
        Node("7", (8, 6)),
        Node("8", (2, 3)),
        Node("9", (2, 10)),
    ]
    graph = Graph_Wrapper(nodes)
    hull = graph.get_hull_nodes()
    assert "4" in hull
    assert "9" in hull
    assert "0" in hull
    assert "5" in hull
    assert "3" in hull
    assert "6" in hull
    assert len(hull) == 6


def test_get_hull_edges():
    # Test the get_hull_edges function
    nodes = [
        Node("0", (5, 10)),
        Node("1", (2, 6)),
        Node("2", (6, 5)),
        Node("3", (9, 3)),
        Node("4", (0, 10)),
        Node("5", (9, 5)),
        Node("6", (1, 2)),
        Node("7", (8, 6)),
        Node("8", (2, 3)),
        Node("9", (2, 10)),
    ]
    graph = Graph_Wrapper(nodes)
    hull = graph.get_hull_edges()
    assert ("4", "9") in hull
    assert ("9", "0") in hull
    assert ("0", "5") in hull
    assert ("5", "3") in hull
    assert ("3", "6") in hull
    assert ("6", "4") in hull
    assert len(hull) == 6


def test_check_if_triangulation_with_degree_constraint():
    nodes = [
        Node("A", (0, 0), 3),
        Node("B", (0, 1), 2),
        Node("C", (1, 0), 2),
        Node("D", (1, 1), 3),
    ]
    graph = Graph_Wrapper(nodes)
    assert not graph.check_if_triangulation_with_degree_constraint()
    graph.add_edge("A", "B")
    graph.add_edge("A", "C")
    graph.add_edge("D", "B")
    graph.add_edge("D", "C")
    assert not graph.check_if_triangulation_with_degree_constraint()
    graph.add_edge("A", "D")
    graph.add_edge("B", "C")
    assert not graph.check_if_triangulation_with_degree_constraint()
    graph.deactivate_edge("B", "C")
    assert graph.check_if_triangulation_with_degree_constraint()
    graph.remove_edge(("B", "D"))
    assert not graph.check_if_triangulation_with_degree_constraint()


def test_check_for_intersection_with_all_edges_and_nodes():
    # Test the check_for_intersection_with_all_edges_and_nodes function
    nodes = [
        Node("A", (0, 0)),
        Node("B", (0, 1)),
        Node("C", (1, 0)),
        Node("D", (1, 1)),
    ]
    graph = Graph_Wrapper(nodes)
    graph.add_convex_hull()
    graph.add_edge("A", "D")
    graph.add_edge("B", "C")
    assert graph.check_for_intersection_with_all_edges_and_nodes(("A", "D"))
    assert not graph.check_for_intersection_with_all_edges_and_nodes(("A", "B"))


def test_get_intersections_with_all_edges():
    nodes = [
        Node("0", (5, 10)),
        Node("1", (2, 6)),
        Node("2", (6, 5)),
        Node("3", (9, 3)),
        Node("4", (0, 10)),
        Node("5", (9, 5)),
        Node("6", (1, 2)),
        Node("7", (8, 6)),
        Node("8", (2, 3)),
        Node("9", (2, 10)),
    ]
    graph = Graph_Wrapper(nodes)
    graph.add_all_possible_edges(True)
    assert graph.get_intersections_with_all_edges(("5", "6")) == [
        ("3", "4"),
        ("3", "8"),
        ("2", "3"),
        ("1", "3"),
        ("3", "7"),
        ("3", "9"),
        ("0", "3"),
    ]

from graph_utils.graph_wrapper import Graph_Wrapper
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
    flipped = graph.flip_edge(("A", "D"))
    assert flipped is True
    assert ("B", "C") in graph.get_all_edges()


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

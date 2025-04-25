from graph_utils.graph_wrapper import Graph_Wrapper
from graph_utils.node import Node


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
    assert flipped is True, "Flip function failed to flip the edge."
    assert ("B", "C") in graph.get_all_edges(), "Edge was not removed after flip."

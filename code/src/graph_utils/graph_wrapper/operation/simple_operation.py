import itertools
from graph_utils.graph_wrapper.data import Data
from graph_utils.graph_wrapper.check import check_edge_intersection_with_nodes


def add_all_possible_edges(data: Data, default_for_active: bool = False) -> None:
    """Fügt alle möglichen Kanten zwischen den Knoten hinzu."""
    combinations = list(itertools.combinations(data.nodes, 2))
    for com in combinations:
        data.add_edge(com[0], com[1], default_for_active)
        if check_edge_intersection_with_nodes(data, (com[0], com[1]), False):
            data.remove_edge((com[0], com[1]))

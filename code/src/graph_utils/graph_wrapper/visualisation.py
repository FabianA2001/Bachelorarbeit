import networkx as nx
import matplotlib.pyplot as plt
from graph_utils import graph_const
import logging
from graph_utils.graph_wrapper.data import Data
from graph_utils.graph_wrapper.file_system import save_graph_as_json
from graph_utils.graph_wrapper.check import Check


def show_and_save(
    data: Data,
    check: Check,
    number_edges_in_Triangulation: int,
    show: bool = True,
    save: bool = True,
    block: bool = False,
) -> None:
    """Zeichnet den Graphen mit den festgelegten Positionen und Farben."""
    logging.info("starte show_and_save")
    local_graph = data.get_aktive_graph()
    num_active_edges = len(local_graph.edges)
    # logging.info(f"aktive kanten: {num_active_edges}")
    if num_active_edges != number_edges_in_Triangulation:
        logging.error(
            f"Anzahl der Kanten in der Triangulation stimmt nicht überein.\nEs sollten {number_edges_in_Triangulation} sein, aber es sind {num_active_edges}."
        )
        save_graph_as_json(data, data.name + "_error.json")

    pos = nx.get_node_attributes(local_graph, "pos")
    degrees = nx.get_node_attributes(local_graph, "degree")

    # Labels mit Degree-Werten erstellen
    labels = {node: f"{node}\n{degree}" for node, degree in degrees.items()}

    # Knotenfarben basierend auf dem Grad erstellen
    colors = [
        graph_const.NODE_COLOR_TRUE
        if degree
        == local_graph.degree(
            # type: ignore
            node
        )
        else graph_const.NODE_COLOR_FALSE
        for node, degree in degrees.items()
    ]

    edge_colors = [
        graph_const.EDGE_COLOR_TRUE
        # Beispielbedingung
        if not check.check_for_intersection_with_all_edges_and_nodes(edge)
        else graph_const.EDGE_COLOR_FALSE
        for edge in local_graph.edges
    ]

    # Zeichne den Graphen
    plt.clf()
    nx.draw(
        local_graph,
        pos=pos,
        labels=labels,
        node_color=colors,
        edge_color=edge_colors,  # Kantenfarben hier festlegen
        node_size=graph_const.NODE_SIZE,
        font_size=graph_const.FONT_SIZE,
    )
    plt.title("Graph mit festen Koordinaten")
    if save:
        plt.savefig(f"{graph_const.FIGURES_PREFIX}{data.name}.pdf")
    if show:
        logging.info("show Graph")
        plt.show(block=block)
    logging.info("ende show_and_save")

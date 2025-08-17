import logging
import os

import matplotlib.pyplot as plt
import networkx as nx

from .. import graph_const
from .check import Check
from .data import Data
from .file_system import save_graph_as_json


def draw(
    data: Data,
    check: Check,
    number_edges_in_Triangulation: int,
    show: bool,
    save: str,
    block: bool,
    draw_name: bool = True,
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
        save_graph_as_json(data, "error/", f"{data.name}_error.json")

    pos = nx.get_node_attributes(local_graph, "pos")
    degrees = nx.get_node_attributes(local_graph, "degree")

    # Labels mit Degree-Werten erstellen
    if draw_name:
        labels = {node: f"{node}\n{degree}" for node, degree in degrees.items()}
    else:
        labels = {node: f"{degree}" for node, degree in degrees.items()}

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
        if not os.path.exists(save):
            os.makedirs(save)
        plt.savefig(f"{save}/{(data.name).replace('/', '_')}.pdf")
    if show:
        logging.info("show Graph")
        plt.show(block=block)
    logging.info("ende show_and_save")


def draw_with_set_false(
    data: Data,
    check: Check,
    number_edges_in_Triangulation: int,
    show: bool,
    save: str,
    block: bool,
    draw_name: bool = True,
    all_green: bool = False,
) -> None:
    """Zeichnet den Graphen mit den festgelegten Positionen und Farben."""
    logging.info("starte show_and_save")
    local_graph = data.get_aktive_graph(True)
    num_active_edges = len(local_graph.edges)
    # logging.info(f"aktive kanten: {num_active_edges}")
    if num_active_edges != number_edges_in_Triangulation:
        logging.error(
            f"Anzahl der Kanten in der Triangulation stimmt nicht überein.\nEs sollten {number_edges_in_Triangulation} sein, aber es sind {num_active_edges}."
        )
        save_graph_as_json(data, "error/", f"{data.name}_error.json")

    pos = nx.get_node_attributes(local_graph, "pos")
    degrees = nx.get_node_attributes(local_graph, "degree")

    # Labels mit Degree-Werten erstellen
    if draw_name:
        labels = {node: f"{node}\n{degree}" for node, degree in degrees.items()}
    else:
        labels = {node: f"{degree}" for node, degree in degrees.items()}

    # Knotenfarben basierend auf dem Grad erstellen
    if not all_green:
        colors = [
            graph_const.NODE_COLOR_TRUE
            if degree
            == len(
                [
                    edge
                    for edge in local_graph.edges(node)
                    if local_graph.edges[edge].get("active")
                ]
            )
            else graph_const.NODE_COLOR_FALSE
            for node, degree in degrees.items()
        ]
    else:
        colors = [graph_const.NODE_COLOR_TRUE for node, degree in degrees.items()]

    # edge_colors = [
    #     graph_const.EDGE_COLOR_TRUE
    #     # Beispielbedingung
    #     if not check.check_for_intersection_with_all_edges_and_nodes(edge)
    #     else graph_const.EDGE_COLOR_FALSE
    #     for edge in local_graph.edges
    # ]
    edge_colors = []
    edge_widths = []
    edge_alphas = []

    for edge in local_graph.edges:
        if local_graph.edges[edge].get("active"):
            if not all_green:
                if not check.check_for_intersection_with_all_edges_and_nodes(edge):
                    edge_colors.append(graph_const.EDGE_COLOR_TRUE)
                else:
                    edge_colors.append(graph_const.EDGE_COLOR_FALSE)
            else:
                edge_colors.append(graph_const.EDGE_COLOR_TRUE)
            edge_widths.append(1.7)  # Normal width for active edges
            edge_alphas.append(1.0)  # Full opacity for active edges
        elif local_graph.edges[edge].get("show_false"):
            edge_colors.append(graph_const.EDGE_COLOR_SET_FALSE)
            edge_widths.append(0.5)  # Thinner width for show_false edges
            edge_alphas.append(
                0.1
            )  # Lower alpha (more transparent) for show_false edges

    # Zeichne den Graphen
    plt.clf()

    # Draw nodes first
    nx.draw_networkx_nodes(
        local_graph,
        pos=pos,
        node_color=colors,  # type: ignore
        node_size=graph_const.NODE_SIZE,
    )

    # Draw edges with different properties
    for i, edge in enumerate(local_graph.edges):
        nx.draw_networkx_edges(
            local_graph,
            pos=pos,
            edgelist=[edge],
            edge_color=edge_colors[i],
            width=edge_widths[i],
            alpha=edge_alphas[i],
        )

    # Draw labels
    nx.draw_networkx_labels(
        local_graph,
        pos=pos,
        labels=labels,
        font_size=graph_const.FONT_SIZE,
    )

    # Remove axes and frame
    plt.axis("off")
    if save:
        if not os.path.exists(save):
            os.makedirs(save)
        plt.savefig(f"{save}/{(data.name).replace('/', '_')}.pdf")
    if show:
        logging.info("show Graph")
        plt.show(block=block)
    logging.info("ende show_and_save")

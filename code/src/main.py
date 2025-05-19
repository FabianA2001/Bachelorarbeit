from graph_utils.graph_wrapper import Graph_Wrapper, save_graph_as_json
from solver.solver import Solver
from graph_utils.node import (
    save_nodes_as_json,
    load_nodes_from_json,
)
from graph_utils import node
import logging
from graph_utils import generate
from solver.delaunay import Delaunay
from graph_utils.node import Node
from solver.ortools import Ortools
from solver.possible import Possible


def test_algo(points):
    logging.info("Start test_algos function.")
    nodes = generate.gen_nodes(points, 100, 100)
    save_nodes_as_json(nodes)
    graph = Graph_Wrapper(nodes)

    solver: Solver = Delaunay(graph)
    solver.solve()
    graph.show_and_save(show=False)
    save_graph_as_json(graph)

    nodes2 = load_nodes_from_json()
    graph2 = Graph_Wrapper(nodes2)

    solver2: Solver = Ortools(graph2)
    solver2.solve()
    graph2.show_and_save()
    logging.info("End test_algos function.")


def custom_points() -> list[Node]:
    nodes = [
        Node("A", (0, 0)),
        Node("B", (0, 1)),
        Node("C", (1, 0)),
        Node("D", (1, 1)),
    ]
    return nodes


def try_find_error_in_possible():
    logging.info("Start run_test function.")
    # for _ in range(30):
    #     nodes = generate.gen_nodes(20, 100, 100)
    #     graph = Graph_Wrapper(nodes)
    #     solver: Solver = Possible(graph)
    #     solver.solve()
    #     graph.show_and_save(show=False, save=False)

    nodes = node.load_nodes_from_json("instance/Possible")
    graph = Graph_Wrapper(nodes)
    graph.add_all_possible_edges(False)
    solver: Solver = Possible(graph)
    solver.solve()
    for edge in graph.get_all_edges():
        if graph.edges[edge]["active"] is True:
            continue
        graph.active_edge(edge)
        if not graph.check_for_intersection_with_all_edges_and_nodes(edge, True):
            print(f"Edge {edge} is possible")
        graph.deactivate_edge(edge)
    graph.show_and_save()
    logging.info("End run_test function.")


def setup_logging():
    # Basis-Logger konfigurieren (falls mehrfach aufgerufen, keine Duplikate)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Entferne ggf. alte Handler (wichtig bei mehrfachen Konfigurationen)
    if logger.hasHandlers():
        logger.handlers.clear()

    # Console Handler – nur INFO
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # File Handler – nur ERROR und höher
    file_handler = logging.FileHandler("error.log", mode="w")
    file_handler.setLevel(logging.ERROR)

    # Einheitliches Format
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Handler hinzufügen
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def main():
    setup_logging()
    logging.info("Start main function.")
    nodes = generate.gen_nodes(20, 100, 100)
    graph = Graph_Wrapper(nodes)
    solver = Delaunay(graph)
    solver.solve()
    graph.show_and_save(show=False)
    graph.name = "Delaunay"
    nodes2 = graph.get_aktive_graph_nodes()
    graph2 = Graph_Wrapper(nodes2)
    graph2.move_node_global()
    solver2 = Ortools(graph2)
    solver2.solve()
    graph2.show_and_save(show=False)
    logging.info("End main function.")


if __name__ == "__main__":
    main()
    # test für commit

from graph_utils.graph_wrapper import Graph_Wrapper
from solver.solver import Solver
from graph_utils.node import (
    save_nodes_as_json,
    load_nodes_from_json,
    save_graph_as_json,
)
import logging
from graph_utils import generate
from solver.delaunay import Delaunay
from graph_utils.node import Node
import random


def test_algos(runs, points):
    logging.info("Start test_algos function.")
    nodes = generate.gen_nodes(30, 100, 100)
    save_nodes_as_json(nodes)
    graph = Graph_Wrapper(nodes)

    solver: Solver = Delaunay(graph)
    graph = solver.solve()
    graph.show_and_save(show=False)
    save_graph_as_json(graph.graph)

    nodes2 = load_nodes_from_json()
    graph2 = Graph_Wrapper(nodes2)

    # solver2: Solver = Ortools(graph2)
    # graph2 = solver2.solve()
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


def random_Flips():
    nodes = load_nodes_from_json()
    nodes = generate.gen_nodes(200, 1000, 1000)
    save_nodes_as_json(nodes)
    # nodes = custom_points()
    graph = Graph_Wrapper(nodes)
    solver = Delaunay(graph)
    solver.solve()
    graph.show_and_save(show=False)
    for i in range(10):
        print(f"Run {i}")
        while True:
            edges = graph.get_all_edges()
            edge = random.choice(edges)
            if graph.flip_edge(edge):
                break
    graph.graph_name = "Flipped_"
    graph.show_and_save(show=False)


def current_test():
    # nodes = load_nodes_from_json()
    nodes = generate.gen_nodes(10, 200, 200)
    save_nodes_as_json(nodes)
    graph = Graph_Wrapper(nodes)
    solver = Delaunay(graph)
    graph = solver.solve()
    graph.show_and_save()


def main():
    logging.info("Start main function.")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )

    # random_Flips()
    # test_algos(10, 20)
    current_test()
    logging.info("End main function.")


if __name__ == "__main__":
    main()

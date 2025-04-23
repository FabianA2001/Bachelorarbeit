from graphe_utils.graphe import Graphe
from solver.solver import Solver
from graphe_utils.node import (
    save_nodes_as_json,
    load_nodes_from_json,
    save_graph_as_json,
)
import logging
from graphe_utils import generate
from solver.delaunay import Delaunay
from graphe_utils.node import Node


def test_algos(runs, points):
    logging.info("Start test_algos function.")
    nodes = generate.gen_nodes(30, 100, 100)
    save_nodes_as_json(nodes)
    graphe = Graphe(nodes)

    solver: Solver = Delaunay(graphe)
    graphe = solver.solve()
    graphe.show_and_save(show=False)
    save_graph_as_json(graphe.graph)

    nodes2 = load_nodes_from_json()
    graphe2 = Graphe(nodes2)

    # solver2: Solver = Ortools(graphe2)
    # graphe2 = solver2.solve()
    graphe2.show_and_save()
    logging.info("End test_algos function.")


def coustom_points() -> list[Node]:
    nodes = [
        Node("A", (0, 0)),
        Node("B", (0, 1)),
        Node("C", (1, 0)),
        Node("D", (1, 1)),
    ]
    return nodes


def main():
    logging.info("Start main function.")
    nodes = load_nodes_from_json()
    # nodes = generate.gen_nodes(10, 100, 100)
    save_nodes_as_json(nodes)
    # nodes = coustom_points()
    graphe = Graphe(nodes)
    solver = Delaunay(graphe)
    solver.solve()
    graphe.flip_edge(("9", "5"))
    graphe.show_and_save()

    logging.info("End main function.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    main()
    # test_algos(10, 20)

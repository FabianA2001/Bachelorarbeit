from graphe_utils.graphe import Graphe
from solver.solver import Solver
from graphe_utils.node import (
    save_nodes_as_json,
    load_nodes_from_json,
    save_graph_as_json,
)
import logging
from graphe_utils import generate


def test_algos(runs, points):
    for _ in range(runs):
        nodes = generate.gen_nodes(points, 100, 100)
        graphe = Graphe(nodes)
        from solver.ortools import Ortools

        solver: Solver = Ortools(graphe)
        solver.solve()
        graphe.show_and_save()
        from solver.possible import Possible

        solver: Solver = Possible(graphe)
        solver.solve()
        graphe.show_and_save()
        print("---------------")


def main():
    logging.info("Start main function.")
    # nodes = load_nodes_from_json()
    nodes = generate.gen_nodes(40, 100, 100)
    save_nodes_as_json(nodes)
    graphe = Graphe(nodes)
    from solver.possible import Possible

    solver: Solver = Possible(graphe)
    graphe = solver.solve()
    graphe.show_and_save(show=False)
    save_graph_as_json(graphe.graph)

    nodes2 = load_nodes_from_json()
    graphe2 = Graphe(nodes2)
    from solver.ortools import Ortools

    solver2: Solver = Ortools(graphe2)
    graphe2 = solver2.solve()
    graphe2.show_and_save()
    logging.info("End main function.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    main()
    # test_algos(10, 20)

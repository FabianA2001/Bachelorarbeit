from graphe_utils.graphe import Graphe
from graphe_utils import generate
from solver.solver import Solver
from solver.ortools import Ortools
from graphe_utils.node import save_Nodes_as_Json, load_Nodes_from_Json
import logging


def main():
    logging.info("Start main function.")
    nodes = load_Nodes_from_Json()
    nodes = generate.gen_nodes(20, 100, 100)
    # nodes = [
    #     Node("1", (0, 0)),
    #     Node("2", (0, 2)),
    #     Node("3", (2, 0)),
    #     Node("4", (2, 2)),
    # ]
    save_Nodes_as_Json(nodes)
    graphe = Graphe(nodes)
    solver: Solver = Ortools(graphe)
    graphe = solver.solve()
    graphe.show_and_save()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    main()

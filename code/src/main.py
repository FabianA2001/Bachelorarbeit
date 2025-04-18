from graphe_utils.graphe import Graphe
from graphe_utils import generate
from solver.solver import Solver
from solver.ortools import Ortools
import logging


def main():
    logging.info("Start main function.")
    nodes = generate.gen_nodes(20, 100, 100)
    # nodes = [
    #     Node("1", (0, 0)),
    #     Node("2", (0, 2)),
    #     Node("3", (2, 0)),
    #     Node("4", (2, 2)),
    # ]
    # save_Nodes_as_Json(nodes)
    # nodes = load_Nodes_from_Json()
    G = Graphe(nodes)
    S: Solver = Ortools(G)
    G = S.solve()
    G.show_and_save()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    main()

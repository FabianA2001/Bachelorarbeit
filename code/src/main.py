from graphe_utils.graphe import Graphe
from solver.solver import Solver
from graphe_utils.node import save_Nodes_as_Json, load_Nodes_from_Json
import logging


def main():
    logging.info("Start main function.")
    nodes = load_Nodes_from_Json()
    # nodes = generate.gen_nodes(50, 100, 100)
    save_Nodes_as_Json(nodes)
    graphe = Graphe(nodes)

    # from solver.ortools import Ortools
    # solver: Solver = Ortools(graphe)
    from solver.possible import Possible

    solver: Solver = Possible(graphe)

    graphe = solver.solve()
    graphe.show_and_save()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    main()

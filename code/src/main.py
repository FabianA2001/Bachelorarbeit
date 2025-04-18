from graphe_utils.graphe import Graphe
from graphe_utils.node import Node
from solver.solver import Solver
from solver.ortools import Ortools


def main():
    # nodes = generate.gen_nodes(50, 100, 100)
    nodes = [
        Node("1", (0, 0)),
        Node("2", (0, 2)),
        Node("3", (2, 0)),
        Node("4", (2, 2)),
    ]
    # save_Nodes_as_Json(nodes)
    # nodes = load_Nodes_from_Json()
    G = Graphe(nodes)
    S: Solver = Ortools()
    G = S.solve(G)
    G.show_and_save()


if __name__ == "__main__":
    main()

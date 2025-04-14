from graphe_utils.graphe import Graphe
from graphe_utils.node import Node
from graphe_utils import generate


def main():
    nodes = generate.gen_nodes(50, 100, 100)
    G = Graphe(nodes)
    G.show_and_save()


if __name__ == "__main__":
    main()

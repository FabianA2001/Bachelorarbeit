from graphe_utils.graphe import Graphe
from graphe_utils.node import Node, save_Nodes_as_Json, load_Nodes_from_Json
from graphe_utils import generate


def main():
    nodes = generate.gen_nodes(50, 100, 100)
    save_Nodes_as_Json(nodes)
    # nodes = load_Nodes_from_Json()
    G = Graphe(nodes)
    G.show_and_save()


if __name__ == "__main__":
    main()

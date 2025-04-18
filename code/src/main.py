from graphe_utils.graphe import Graphe
from graphe_utils.node import load_Nodes_from_Json


def main():
    # nodes = generate.gen_nodes(50, 100, 100)
    # save_Nodes_as_Json(nodes)
    nodes = load_Nodes_from_Json()
    G = Graphe(nodes)
    G.add_edge("48", "16")
    G.add_edge("39", "44")
    G.add_edge("1", "21")
    G.show_and_save()


if __name__ == "__main__":
    main()

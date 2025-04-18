from graphe_utils.graphe import Graphe
from graphe_utils.node import Node


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
    G.add_all_possible_edges()
    G.deactivate_edge("1", "4")
    G.show_and_save()


if __name__ == "__main__":
    main()

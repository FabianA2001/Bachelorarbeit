from Graphe import Graphe, Node


def main():
    nodes = [
        Node('A', (0, 0), 1),
        Node('B', (1, 1), 2),
        Node('C', (1, -1), 2),
        Node('D', (2, 0), 3),
    ]
    G = Graphe(nodes)
    G.add_edge('A', 'B')
    G.add_edge('B', 'C')
    G.show_and_save()


if __name__ == "__main__":
    main()

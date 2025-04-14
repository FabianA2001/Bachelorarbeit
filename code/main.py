from Graphe import Graphe


def main():
    nodes = {
        'A': (0, 0),
        'B': (1, 1),
        'C': (2, 0),
        'D': (1, -1)}
    G = Graphe(nodes)
    G.add_edge('A', 'B')
    G.add_edge('B', 'C')
    G.show_and_save()


if __name__ == "__main__":
    main()

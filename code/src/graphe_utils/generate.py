from random import randint
from graphe_utils.node import Node
from graphe_utils import graphe_const


def gen_nodes(
    n: int = 10,
    width: int = graphe_const.GEN_WIDTH,
    height: int = graphe_const.GEN_HEIGHT,
) -> list[Node]:
    """Generiert eine Liste von Knoten mit zufälligen Positionen und Graden."""
    nodes = []
    posis = []
    for i in range(n):
        while True:
            pos = (randint(0, width), randint(0, height))
            if pos not in posis:
                posis.append(pos)
                break
        nodes.append(Node(str(i), pos))
    return nodes

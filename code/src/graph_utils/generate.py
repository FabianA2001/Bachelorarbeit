from random import randint
from graph_utils.node import Node
from graph_utils import graph_const


def gen_nodes(
    n: int = 10,
    width: int = graph_const.GEN_WIDTH,
    height: int = graph_const.GEN_HEIGHT,
) -> list[Node]:
    """Generiert eine Liste von Knoten mit zufälligen Positionen und Graden."""
    nodes = []
    poss = []
    for i in range(n):
        while True:
            pos = (randint(0, width), randint(0, height))
            if pos not in poss:
                poss.append(pos)
                break
        nodes.append(Node(str(i), pos))
    return nodes

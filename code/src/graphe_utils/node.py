from graphe_utils import graphe_const
import json
import networkx as nx


class Node:
    def __init__(self, name: str, pos: tuple[int, int], degree: int = -1) -> None:
        self.name = name
        self.pos = pos
        self.degree = degree

    def __str__(self) -> str:
        return f"{self.name} ({self.pos[0]}, {self.pos[1]})"

    def __repr__(self) -> str:
        return f"Node({self.name}, {self.pos})"


def save_nodes_as_json(
    Nodes: list[Node], filename: str = graphe_const.DEFAULT_FILE_NAME
) -> None:
    """Speichert eine Liste von Knoten in einer JSON-Datei."""
    with open(f"{graphe_const.PREFIX_INSTANCE}{filename}.json", "w") as f:
        json.dump([node.__dict__ for node in Nodes], f, indent=4)


def load_nodes_from_json(filename: str = graphe_const.DEFAULT_FILE_NAME) -> list[Node]:
    """Lädt eine Liste von Knoten aus einer JSON-Datei."""
    with open(f"{graphe_const.PREFIX_INSTANCE}{filename}.json", "r") as f:
        data = json.load(f)
        nodes = [Node(**node) for node in data]
    return nodes


def save_graph_as_json(
    graph: nx.Graph, filename: str = graphe_const.DEFAULT_FILE_NAME
) -> None:
    local_grphe = graph.copy()
    for edge in local_grphe.edges:
        if local_grphe.edges[edge].get("active") is False:
            local_grphe.remove_edge(edge[0], edge[1])

    nodes = []
    for node in local_grphe.nodes:
        nodes.append(
            Node(
                node, local_grphe.nodes[node]["pos"], len(list(local_grphe.edges(node)))
            )
        )
    save_nodes_as_json(nodes, filename)

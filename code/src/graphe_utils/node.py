from graphe_utils import graphe_const
import json


class Node:
    def __init__(self, name: str, pos: tuple[int, int], degree: int = 0) -> None:
        self.name = name
        self.pos = pos
        self.degree = degree

    def __str__(self) -> str:
        return f"{self.name} ({self.pos[0]}, {self.pos[1]})"

    def __repr__(self) -> str:
        return f"Node({self.name}, {self.pos})"


def save_Nodes_as_Json(
    Nodes: list[Node], filename: str = graphe_const.DEFAULT_FILE_NAME
) -> None:
    """Speichert eine Liste von Knoten in einer JSON-Datei."""
    with open(f"{graphe_const.PREFIX_INSTANCE}{filename}.json", "w") as f:
        json.dump([node.__dict__ for node in Nodes], f, indent=4)


def load_Nodes_from_Json(filename: str = graphe_const.DEFAULT_FILE_NAME) -> list[Node]:
    """Lädt eine Liste von Knoten aus einer JSON-Datei."""
    with open(f"{graphe_const.PREFIX_INSTANCE}{filename}.json", "r") as f:
        data = json.load(f)
        nodes = [Node(**node) for node in data]
    return nodes

from graph_utils import graph_const
import json
import os
import random
import logging


class Node:
    def __init__(self, name: str, pos: tuple[int, int], degree: int = -1) -> None:
        self.name = name
        self.pos: tuple[int, int] = pos
        self.degree = degree

    def __str__(self) -> str:
        return f"{self.name}\tp:({self.pos[0]}, {self.pos[1]})\td:{self.degree}"

    def __repr__(self) -> str:
        return f"Node({self.name}, {self.pos})"


def save_nodes_as_json(
    Nodes: list[Node], filename: str = graph_const.DEFAULT_FILE_NAME
) -> None:
    path = f"{graph_const.PREFIX_INSTANCE}{filename}"
    """Speichert eine Liste von Knoten in einer JSON-Datei."""
    # Erstelle den Ordner, falls er nicht existiert
    path_list = path.split("/")
    pre_path = ""
    # print(path_list)
    for directory in path_list[:-1]:
        if not os.path.exists(pre_path + directory):
            os.makedirs(pre_path + directory)
        pre_path += f"{directory}/"

    # Speichere die Knoten in der JSON-Datei
    with open(path, "w") as f:
        data = {}
        data["nodes"] = [node.__dict__ for node in Nodes]
        json.dump(data, f, indent=4)


def load_nodes_from_json(filename: str = graph_const.DEFAULT_FILE_PATH) -> list[Node]:
    """Lädt eine Liste von Knoten aus einer JSON-Datei."""
    with open(f"{graph_const.PREFIX_INSTANCE}{filename}", "r") as f:
        data = json.load(f)["nodes"]
        nodes = [
            Node(node["name"], tuple(node["pos"]), node.get("degree", -1))
            for node in data
        ]
    return nodes


def move_degree(
    nodes: list[Node], amount: int = 1, degree_min: int = 1, degree_max: int = 10
) -> list[Node]:
    def __move_degree(nodes: list[Node], degree: int = 1) -> list[Node]:
        """Bewege die Knoten mit dem angegebenen Grad."""
        if nodes is None or len(nodes) == 0:
            raise ValueError("Node list is empty")
        if degree < 1:
            raise ValueError("Degree must be greater than or equal to 1")
        for _ in range(100):
            node1 = random.choice(nodes)
            node2 = random.choice(nodes)
            if node1 == node2:
                continue
            if node1.degree == -1 or node2.degree == -1:
                continue
            if node1.degree < degree:
                continue
            node1.degree -= degree
            node2.degree += degree
            logging.info(
                f"Moved {degree} degree from node {node1.name} to node {node2.name}"
            )
            return nodes
        raise ValueError("No nodes with degree found")

    for _ in range(amount):
        nodes = __move_degree(nodes, random.randint(degree_min, degree_max))
    return nodes

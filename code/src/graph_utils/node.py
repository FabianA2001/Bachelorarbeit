from graph_utils import graph_const
import json
import os


class Node:
    def __init__(self, name: str, pos: tuple[int, int], degree: int = -1) -> None:
        self.name = name
        self.pos: tuple[int, int] = pos
        self.degree = degree

    def __str__(self) -> str:
        return f"{self.name} ({self.pos[0]}, {self.pos[1]})"

    def __repr__(self) -> str:
        return f"Node({self.name}, {self.pos})"


def save_nodes_as_json(
    Nodes: list[Node], filename: str = graph_const.DEFAULT_FILE_NAME
) -> None:
    path = f"{graph_const.PREFIX_INSTANCE}{filename}.json"
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
    with open(f"{filename}.json", "r") as f:
        data = json.load(f)["nodes"]
        nodes = [
            Node(node["name"], tuple(node["pos"]), node.get("degree", -1))
            for node in data
        ]
    return nodes

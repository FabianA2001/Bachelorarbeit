import json
import logging
import math
import os
from abc import ABC, abstractmethod
from random import choice, randint
from typing import Optional

from ..solver.delaunay import Delaunay
from ..solver.greedy import Greedy
from ..solver.iterative import Iterative
from ..solver.random_adder import Random_Adder
from . import graph_const
from .graph_wrapper.graph_wrapper import Graph_Wrapper
from .node import Node, save_nodes_as_json


def gen_nodes(
    n: int = 10,
    width: int = graph_const.GEN_WIDTH,
    height: int = graph_const.GEN_HEIGHT,
) -> list[Node]:
    """Generiert eine Liste von Knoten mit zufälligen Positionen und Graden."""
    nodes = []
    poss = []
    for i in range(n):
        for _ in range(500):
            pos = (randint(0, width), randint(0, height))
            if pos not in poss:
                poss.append(pos)
                break
        nodes.append(Node(pos))
    return nodes


class Generate_Instance_ABC_Edges(ABC):
    @abstractmethod
    def generate_instance(self, graph: Graph_Wrapper) -> tuple[list[Node], bool]:
        """Generiert eine Instanz des Graphen mit den gegebenen Knoten."""
        pass


class Generate_Instance_ABC_Nodes(ABC):
    @abstractmethod
    def generate_nodes(
        self,
        number_nodes: int,
        width: int = graph_const.GEN_WIDTH,
        height: int = graph_const.GEN_HEIGHT,
    ) -> list[Node]:
        """Generiert eine Liste von Knoten mit zufälligen Positionen und Graden."""
        pass


class Generate_Make_Impossible(ABC):
    @abstractmethod
    def generate_instance(self, nodes: list[Node]) -> tuple[list[Node], bool]:
        """Generiert eine Instanz des Graphen mit den gegebenen Knoten."""
        pass


class Generate_Instance:
    def __init__(
        self,
        name: str,
        file_name: str,
        number_nodes: int,
        number_instances: int,
        nodes_gen: Generate_Instance_ABC_Nodes,
        edges_gen: Generate_Instance_ABC_Edges,
        impossible_gen: Optional[Generate_Make_Impossible] = None,
        path: str = "",
        width: int = graph_const.GEN_WIDTH,
        height: int = graph_const.GEN_HEIGHT,
    ) -> None:
        self.name = name
        self.file_name = file_name
        self.number_nodes = number_nodes
        self.number_instances = number_instances
        self.nodes_gen = nodes_gen
        self.edges_gen = edges_gen
        self.impossible_gen = impossible_gen
        self.path = path
        self.width = width
        self.height = height

    def generate(self) -> None:
        if self.file_name == "":
            raise ValueError("lokal_name is not set.")
        for _ in range(self.number_instances):
            nodes = self.nodes_gen.generate_nodes(
                self.number_nodes, self.width, self.height
            )
            graph = Graph_Wrapper(nodes)
            nodes, possible = self.edges_gen.generate_instance(graph)
            if self.impossible_gen is not None:
                nodes, possible = self.impossible_gen.generate_instance(nodes)
            if os.path.exists(os.path.join(self.path, self.name)):
                number_files = len(
                    [
                        name
                        for name in os.listdir(os.path.join(self.path, self.name))
                        if ".json" in name
                    ]
                )
            else:
                number_files = 0
            number = str(number_files).zfill(3)
            filename = f"{self.name}/{number}_{self.file_name}_{len(graph.get_all_nodes())}.json"
            save_nodes_as_json(
                nodes,
                path=self.path,
                filename=filename,
            )
            if possible is not None:
                path = os.path.join(self.path, filename)
                with open(path, "r") as f:
                    data = json.load(f)
                data["possible"] = possible
                with open(path, "w") as f:
                    json.dump(data, f, indent=4)


class Generate_Edges_Delaunay_Flips(Generate_Instance_ABC_Edges):
    def __init__(self, number_flips) -> None:
        assert number_flips > 0, "Number of flips must be greater than 0."
        self.number_flips = number_flips

    def generate_instance(
        self, graph: Graph_Wrapper
    ) -> tuple[list[Node], Optional[bool]]:
        solver = Delaunay(graph)
        solver.solve(
            {
                "timeout": 60,
                "ignore_degree": True,
            }
        )
        for _ in range(self.number_flips):
            while True:
                edges = graph.get_all_edges()
                edge = choice(edges)
                if graph.flip_edge(edge):
                    break
        return (graph.get_aktive_graph_nodes(), True)


class Generate_Edges_Delaunay(Generate_Instance_ABC_Edges):
    def generate_instance(
        self, graph: Graph_Wrapper
    ) -> tuple[list[Node], Optional[bool]]:
        solver = Delaunay(graph)
        solver.solve(
            {
                "timeout": -1,
                "ignore_degree": True,
            }
        )
        return (graph.get_aktive_graph_nodes(), True)


class Generate_Edges_Random(Generate_Instance_ABC_Edges):
    def generate_instance(
        self, graph: Graph_Wrapper
    ) -> tuple[list[Node], Optional[bool]]:
        solver = Random_Adder(graph)
        solver.solve(
            {
                "timeout": -1,
                "ignore_degree": True,
            }
        )
        return (graph.get_aktive_graph_nodes(), True)


class Generate_Edges_Greedy(Generate_Instance_ABC_Edges):
    def generate_instance(
        self, graph: Graph_Wrapper
    ) -> tuple[list[Node], Optional[bool]]:
        solver = Greedy(graph)
        solver.solve(
            {
                "timeout": -1,
                "ignore_degree": True,
            }
        )
        return (graph.get_aktive_graph_nodes(), True)


class Generate_Edges_Iterative(Generate_Instance_ABC_Edges):
    def generate_instance(
        self, graph: Graph_Wrapper
    ) -> tuple[list[Node], Optional[bool]]:
        solver = Iterative(graph)
        solver.solve(
            {
                "timeout": -1,
                "ignore_degree": True,
            }
        )
        return (graph.get_aktive_graph_nodes(), True)


class Generate_Nodes_Iterativ(Generate_Instance_ABC_Nodes):
    def __init__(self, step: int, number_instance: int) -> None:
        self.step = step
        self.round = number_instance - 1

    def generate_nodes(
        self,
        number_nodes: int,
        width: int = graph_const.GEN_WIDTH,
        height: int = graph_const.GEN_HEIGHT,
    ) -> list[Node]:
        """Generiert eine Liste von Knoten mit zufälligen Positionen und Graden."""
        number_nodes = number_nodes - self.step * self.round
        self.round -= 1
        return gen_nodes(number_nodes, width, height)


class Generate_Nodes_Given(Generate_Instance_ABC_Nodes):
    def __init__(self, nodes: list[Node]) -> None:
        """Initialisiert die Klasse mit einer Liste von Knoten."""
        self.nodes = nodes

    def generate_nodes(
        self,
        number_nodes: int,
        width: int = graph_const.GEN_WIDTH,
        height: int = graph_const.GEN_HEIGHT,
    ) -> list[Node]:
        """Generiert eine Liste von Knoten mit zufälligen Positionen und Graden."""
        return self.nodes


class Generate_Nodes_Random(Generate_Instance_ABC_Nodes):
    def generate_nodes(
        self,
        number_nodes: int,
        width: int = graph_const.GEN_WIDTH,
        height: int = graph_const.GEN_HEIGHT,
    ) -> list[Node]:
        """Generiert eine Liste von Knoten mit zufälligen Positionen und Graden."""
        return gen_nodes(number_nodes, width, height)


class Generate_Nodes_n_gon(Generate_Instance_ABC_Nodes):
    def __init__(self, radius: int) -> None:
        """Generiert Knoten in einem n-Eck."""
        self.radius = radius

    def generate_nodes(
        self,
        number_nodes: int,
        width: int = graph_const.GEN_WIDTH,
        height: int = graph_const.GEN_HEIGHT,
    ) -> list[Node]:
        angle = 2 * math.pi / number_nodes
        center_x = width // 2
        center_y = height // 2

        nodes = []
        for i in range(number_nodes):
            x: int = int(center_x + math.cos(i * angle) * self.radius)
            y: int = int(center_y + math.sin(i * angle) * self.radius)
            nodes.append(Node((x, y)))
        return nodes


class Generate_Nodes_Iterativ_N_Gon(Generate_Instance_ABC_Nodes):
    def __init__(self, step: int, number_instance: int, radius: int) -> None:
        self.step = step
        self.round = number_instance
        self.radius = radius

    def generate_nodes(
        self,
        number_nodes: int,
        width: int = graph_const.GEN_WIDTH,
        height: int = graph_const.GEN_HEIGHT,
    ) -> list[Node]:
        """Generiert eine Liste von Knoten mit zufälligen Positionen und Graden."""
        number_nodes = number_nodes - self.step * self.round
        self.round -= 1
        return self.__n_gone(number_nodes, width, height)

    def __n_gone(self, number_nodes, width, height):
        angle = 2 * math.pi / number_nodes
        center_x = width // 2
        center_y = height // 2

        nodes = []
        for i in range(number_nodes):
            x: int = int(center_x + math.cos(i * angle) * self.radius)
            y: int = int(center_y + math.sin(i * angle) * self.radius)
            nodes.append(Node((x, y)))
        return nodes


class Generate_Impossible_Move_Degree(Generate_Make_Impossible):
    def __init__(self, amount: int = 1, times: int = 1) -> None:
        super().__init__()
        self.amount = amount
        self.times = times

    def generate_instance(self, nodes: list[Node]) -> tuple[list[Node], bool]:
        """Generiert eine Instanz des Graphen mit den gegebenen Knoten."""
        blacklist = []
        length_nodes = len(nodes)
        for _ in range(self.times):
            for _ in range(1000):
                node1: Node = choice(nodes)
                node2: Node = choice(nodes)
                lokal_amount = randint(1, self.amount)
                if node1 == node2:
                    continue
                if node1.degree < lokal_amount + 2:
                    continue
                if node2.degree + lokal_amount > length_nodes - 1:
                    continue
                if node1 in blacklist or node2 in blacklist:
                    continue
                blacklist.append(node1)
                blacklist.append(node2)
                node1.degree -= lokal_amount
                node2.degree += lokal_amount
                break
            else:
                logging.warning(
                    "No nodes could be modified to make the graph impossible."
                )

        return (nodes, False)


class Generate_Impossible_Change_Degree(Generate_Make_Impossible):
    def __init__(self, times: int = 1) -> None:
        super().__init__()
        self.times = times

    def generate_instance(self, nodes: list[Node]) -> tuple[list[Node], bool]:
        """Generiert eine Instanz des Graphen mit den gegebenen Knoten."""
        blacklist = []
        for _ in range(self.times):
            for _ in range(1000):
                node1: Node = choice(nodes)
                node2: Node = choice(nodes)
                if node1 in blacklist or node2 in blacklist:
                    continue
                blacklist.append(node1)
                blacklist.append(node2)
                node1.degree, node2.degree = node2.degree, node1.degree
                break
            else:
                logging.warning(
                    "No nodes could be modified to make the graph impossible."
                )

        return (nodes, False)

from random import randint
from graph_utils.node import Node
from graph_utils import graph_const
from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from solver.delaunay import Delaunay
from random import choice
from abc import ABC, abstractmethod
from typing import Optional
import json


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
        nodes.append(Node(str(i), pos))
    return nodes


class Generate_Instance_ABC_Edges(ABC):
    @abstractmethod
    def generate_instance(self, graph: Graph_Wrapper) -> tuple[Graph_Wrapper, bool]:
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


class Generate_Instance:
    def __init__(
        self,
        name: str,
        file_name: str,
        number_nodes: int,
        number_instances: int,
        nodes_gen: Generate_Instance_ABC_Nodes,
        edges_gen: Generate_Instance_ABC_Edges,
        width: int = graph_const.GEN_WIDTH,
        height: int = graph_const.GEN_HEIGHT,
    ) -> None:
        self.name = name
        self.file_name = file_name
        self.number_nodes = number_nodes
        self.number_instances = number_instances
        self.nodes_gen = nodes_gen
        self.edges_gen = edges_gen
        self.width = width
        self.height = height

    def generate(self) -> None:
        if self.file_name == "":
            raise ValueError("lokal_name is not set.")
        for i in range(self.number_instances):
            nodes = self.nodes_gen.generate_nodes(
                self.number_nodes, self.width, self.height
            )
            graph = Graph_Wrapper(nodes)
            graph, possible = self.edges_gen.generate_instance(graph)
            number = str(i).zfill(3)
            graph.save_graph_as_json(f"{self.name}/{number}_{self.file_name}.json")
            if possible is not None:
                path = f"{graph_const.PREFIX_INSTANCE}{self.name}/{number}_{self.file_name}.json"
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
    ) -> tuple[Graph_Wrapper, Optional[bool]]:
        solver = Delaunay(graph)
        solver.solve()
        for _ in range(self.number_flips):
            while True:
                edges = graph.get_all_edges()
                edge = choice(edges)
                if graph.flip_edge(edge):
                    break
        return (graph, True)


class Generate_Edges_Delaunay(Generate_Instance_ABC_Edges):
    def generate_instance(
        self, graph: Graph_Wrapper
    ) -> tuple[Graph_Wrapper, Optional[bool]]:
        solver = Delaunay(graph)
        solver.solve()
        return (graph, True)


class Generate_Nodes_Iterativ(Generate_Instance_ABC_Nodes):
    def __init__(self, step: int, number_instance: int) -> None:
        self.step = step
        self.round = number_instance

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


class Generate_Nodes_Random(Generate_Instance_ABC_Nodes):
    def generate_nodes(
        self,
        number_nodes: int,
        width: int = graph_const.GEN_WIDTH,
        height: int = graph_const.GEN_HEIGHT,
    ) -> list[Node]:
        """Generiert eine Liste von Knoten mit zufälligen Positionen und Graden."""
        return gen_nodes(number_nodes, width, height)

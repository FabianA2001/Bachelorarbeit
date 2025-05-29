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


class Generate_Instance(ABC):
    def __init__(
        self,
        name: str,
        number_nodes: int,
        number_instances: int,
        width: int = graph_const.GEN_WIDTH,
        height: int = graph_const.GEN_HEIGHT,
    ) -> None:
        self.name = name
        self.lokal_name = ""
        self.number_nodes = number_nodes
        self.number_instances = number_instances
        self.width = width
        self.height = height

    def generate(self) -> None:
        if self.lokal_name == "":
            raise ValueError("lokal_name is not set.")
        for i in range(self.number_instances):
            nodes = self._generate_nodes()
            graph = Graph_Wrapper(nodes)
            graph, possible = self._generate_instance(graph)
            number = str(i).zfill(3)
            graph.save_graph_as_json(f"{self.name}/{number}_{self.lokal_name}.json")
            if possible is not None:
                path = f"{graph_const.PREFIX_INSTANCE}{self.name}/{number}_{self.lokal_name}.json"
                with open(path, "r") as f:
                    data = json.load(f)
                data["possible"] = possible
                with open(path, "w") as f:
                    json.dump(data, f, indent=4)

    @abstractmethod
    def _generate_instance(
        self, graph: Graph_Wrapper
    ) -> tuple[Graph_Wrapper, Optional[bool]]: ...

    def _generate_nodes(self) -> list[Node]:
        """Generiert eine Liste von Knoten mit zufälligen Positionen und Graden."""
        return gen_nodes(self.number_nodes, self.width, self.height)


class Generate_Delaunay_Flips(Generate_Instance):
    def __init__(
        self,
        name: str,
        number_nodes: int,
        number_instances: int,
        number_flips: int = 50,
        width: int = graph_const.GEN_WIDTH,
        height: int = graph_const.GEN_HEIGHT,
    ) -> None:
        super().__init__(name, number_nodes, number_instances, width, height)
        self.lokal_name = "delaunay_flips"
        self.number_flips = number_flips

    def _generate_instance(
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


class Generate_Delaunay(Generate_Instance):
    def __init__(
        self,
        name: str,
        number_nodes: int,
        number_instances: int,
        width: int = graph_const.GEN_WIDTH,
        height: int = graph_const.GEN_HEIGHT,
    ) -> None:
        super().__init__(name, number_nodes, number_instances, width, height)
        self.lokal_name = "delaunay"

    def _generate_instance(
        self, graph: Graph_Wrapper
    ) -> tuple[Graph_Wrapper, Optional[bool]]:
        solver = Delaunay(graph)
        solver.solve()
        return (graph, True)


class Generate_Delaunay_Iterativ(Generate_Instance):
    def __init__(
        self,
        name: str,
        number_nodes: int,
        number_instances: int,
        step: int = 1,
        width: int = graph_const.GEN_WIDTH,
        height: int = graph_const.GEN_HEIGHT,
    ) -> None:
        assert step > 0, "Step must be greater than 0."
        assert number_nodes > 0, "Number of nodes must be greater than 0."
        assert number_instances > 0, "Number of instances must be greater than 0."
        assert number_nodes >= step * number_instances
        super().__init__(name, number_nodes, number_instances, width, height)
        self.lokal_name = "delaunay_iterativ"
        self.step = step
        self.round = self.number_instances

    def _generate_instance(
        self, graph: Graph_Wrapper
    ) -> tuple[Graph_Wrapper, Optional[bool]]:
        solver = Delaunay(graph)
        solver.solve()
        return (graph, True)

    def _generate_nodes(self) -> list[Node]:
        """Generiert eine Liste von Knoten mit zufälligen Positionen und Graden."""
        number_nodes = self.number_nodes - self.step * self.round
        self.round -= 1
        return gen_nodes(number_nodes, self.width, self.height)

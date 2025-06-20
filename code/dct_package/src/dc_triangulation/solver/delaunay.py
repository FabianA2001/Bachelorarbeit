import logging

from scipy.spatial import Delaunay as ScipyDelaunay

from ..graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from .solver import Solver


class Delaunay(Solver):
    NAME = "Delaunay"

    def __init__(self, graph: Graph_Wrapper) -> None:
        super().__init__(graph)
        logging.warning("Kein Timeout")
        self.name = self.NAME

    def _actual_solver(self, parameter: dict) -> dict:
        if self.graph is None:
            raise ValueError("Graph is not set. Please set the graph before solving.")

        assert self.graph.get_all_edges() == [], (
            "Graph is not empty. Please clear the graph before solving."
        )

        # Implement Delaunay triangulation algorithm here
        nodes_name = self.graph.get_all_nodes()
        nodes_as_pos = [self.graph._data.nodes[name].get("pos") for name in nodes_name]
        triangles = ScipyDelaunay(nodes_as_pos)
        for tri in triangles.simplices:
            self.graph.add_edge(nodes_name[tri[0]], nodes_name[tri[1]])
            self.graph.add_edge(nodes_name[tri[1]], nodes_name[tri[2]])
            self.graph.add_edge(nodes_name[tri[2]], nodes_name[tri[0]])

        return {
            "success": True,
        }

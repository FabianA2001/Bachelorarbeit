from solver.solver import Solver
from scipy.spatial import Delaunay as ScipyDelaunay
from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from time import sleep


class Delaunay(Solver):
    def __init__(self, graph: Graph_Wrapper) -> None:
        super().__init__(graph)
        self.name = "Delaunay"
        self.version = "0.1"

    def _actual_solver(self, timeout, queue) -> None:
        sleep(0.1)  # Simulate some processing time
        if self.graph is None:
            raise ValueError("Graph is not set. Please set the graph before solving.")

        assert (
            self.graph.get_all_edges() == []
        ), "Graph is not empty. Please clear the graph before solving."

        # Implement Delaunay triangulation algorithm here
        nodes_name = self.graph.get_all_nodes_name()
        nodes_as_pos = [self.graph._data.nodes[name].get("pos") for name in nodes_name]
        triangles = ScipyDelaunay(nodes_as_pos)
        edges = []
        for tri in triangles.simplices:
            edges.append((nodes_name[tri[0]], nodes_name[tri[1]]))
            edges.append((nodes_name[tri[1]], nodes_name[tri[2]]))
            edges.append((nodes_name[tri[2]], nodes_name[tri[0]]))
        queue.put(edges)
        queue.put(False)

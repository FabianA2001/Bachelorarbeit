from solver.solver import Solver
from scipy.spatial import Delaunay as ScipyDelaunay
from time import sleep


class Delaunay(Solver):
    def __init__(self, graph=None) -> None:
        super().__init__(graph)
        self.name = "Delaunay"

    def _actual_solver(self):
        sleep(0.1)  # Simulate some processing time
        if self.graph is None:
            raise ValueError(
                "Graph is not set. Please set the graph before solving.")
        # Implement Delaunay triangulation algorithm here
        nodes_name = self.graph.get_all_nodes_name()
        nodes_as_pos = [self.graph.data.nodes[name].get(
            "pos") for name in nodes_name]
        triangles = ScipyDelaunay(nodes_as_pos)

        for tri in triangles.simplices:
            self.graph.add_edge(
                nodes_name[tri[0]], nodes_name[tri[1]], active=True)
            self.graph.add_edge(
                nodes_name[tri[1]], nodes_name[tri[2]], active=True)
            self.graph.add_edge(
                nodes_name[tri[2]], nodes_name[tri[0]], active=True)

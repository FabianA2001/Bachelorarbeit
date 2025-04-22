from solver.solver import Solver
from scipy.spatial import Delaunay as ScipyDelaunay


class Delaunay(Solver):
    def __init__(self, graph) -> None:
        super().__init__(graph)
        self.name = "Delaunay"

    def _actual_solver(self):
        # Implement Delaunay triangulation algorithm here
        nodes_name = self.graph.get_all_nodes_name()
        nodes_as_pos = [self.graph.graph.nodes[name].get(
            "pos") for name in nodes_name]
        tris = ScipyDelaunay(nodes_as_pos)

        for tri in tris.simplices:
            self.graph.add_edge(
                nodes_name[tri[0]], nodes_name[tri[1]], active=True
            )
            self.graph.add_edge(
                nodes_name[tri[1]], nodes_name[tri[2]], active=True
            )
            self.graph.add_edge(
                nodes_name[tri[2]], nodes_name[tri[0]], active=True
            )

from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from solver.solver import Solver
import shapely
import itertools


class Possible(Solver):
    def __init__(self, graph: Graph_Wrapper) -> None:
        super().__init__(graph)
        self.name = "Possible"

    def find_nearest_point(self, point: shapely.Point) -> shapely.Point:
        nearest_point = min(self.points, key=lambda p: point.distance(p))
        return nearest_point

    def _actual_solver(self) -> bool:
        if not isinstance(self.graph, Graph_Wrapper):
            raise ValueError("Graph is not set. Please set the graph before solving.")

        self.points = [attr["point"] for _, attr in self.graph.data.nodes(data=True)]
        self.graph.add_convex_hull()

        combinations = itertools.combinations(self.points, 2)
        for point1, point2 in combinations:
            line = shapely.LineString([point1, point2])
            if not self.graph.check_for_intersection_with_all_edges_and_nodes(line):
                self.graph.add_edge(
                    self.graph.get_node_from_point(point1),
                    self.graph.get_node_from_point(point2),
                    True,
                )
        return True

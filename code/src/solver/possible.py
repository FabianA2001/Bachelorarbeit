from graphe_utils.graphe import Graphe
from solver.solver import Solver
import shapely
import itertools


class Possible(Solver):
    def __init__(self, graph: Graphe) -> None:
        super().__init__(graph)
        self.name = "Possible"
        self.points = [attr["point"] for _, attr in self.graph.graph.nodes(data=True)]

    def find_nearest_point(self, point: shapely.Point) -> shapely.Point:
        nearest_point = min(self.points, key=lambda p: point.distance(p))
        return nearest_point

    def actual_solver(self):
        combinations = itertools.combinations(self.points, 2)
        for point1, point2 in combinations:
            line = shapely.LineString([point1, point2])
            if not self.graph.check_for_intersection_with_all_edges(line):
                self.graph.add_edge(
                    self.graph.get_node_from_point(point1),
                    self.graph.get_node_from_point(point2),
                    True,
                )

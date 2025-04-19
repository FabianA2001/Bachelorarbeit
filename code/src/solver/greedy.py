from graphe_utils.graphe import Graphe
from solver.solver import Solver
import shapely


class Greedy(Solver):
    def __init__(self, graph: Graphe) -> None:
        super().__init__(graph)
        self.points = [attr["point"] for _, attr in self.graph.graph.nodes(data=True)]

    def find_nearest_point(self, point: shapely.Point) -> shapely.Point:
        nearest_point = min(self.points, key=lambda p: point.distance(p))
        return nearest_point

    def actual_solver(self):
        point1 = self.points[0]
        self.points.remove(point1)
        while self.points:
            while True:
                point2 = self.find_nearest_point(point1)
                if not self.graph.check_for_intersection_with_all_edges(
                    shapely.LineString([point1, point2]), check_if_active=False
                ):
                    break
            self.graph.add_edge(
                self.graph.point_to_node[point1], self.graph.point_to_node[point2], True
            )
            point1 = point2
            self.points.remove(point1)

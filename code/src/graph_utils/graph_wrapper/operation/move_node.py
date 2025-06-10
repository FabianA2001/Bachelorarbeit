import shapely
import logging
import random
from graph_utils.graph_wrapper.data import Data


class No_Solution_Error(Exception):
    pass


def move_node(data: Data, node: int = 0, distance: int = -1) -> bool:
    # if distance == -1: Global bewegen
    def global_move() -> tuple[shapely.Point, tuple[int, int]]:
        MULTIPLIER_MAX = 1.2
        MULTIPLIER_MIN = 0.8
        min_x, min_y, max_y, max_x = 0, 0, 0, 0
        for point in points:
            if point.x < min_x:
                min_x = point.x
            if point.y < min_y:
                min_y = point.y
            if point.x > max_x:
                max_x = point.x
            if point.y > max_y:
                max_y = point.y
        for _ in range(100):
            x = random.randint(int(min_x * MULTIPLIER_MIN), int(max_x * MULTIPLIER_MAX))
            y = random.randint(int(min_y * MULTIPLIER_MIN), int(max_y * MULTIPLIER_MAX))
            if x < 0 or y < 0:
                continue
            point = shapely.geometry.Point(x, y)
            if multipoint.intersects(point):
                continue
            return point, (x, y)
        raise No_Solution_Error

    if node == "":
        node = data.get_all_nodes_name[random.randint(0, len(data.nodes) - 1)]
    points = [attr["point"] for _, attr in data.nodes(data=True)]
    multipoint = shapely.geometry.MultiPoint(points)

    def lokal_move(distance: int) -> tuple[shapely.Point, tuple[int, int]]:
        pre_x, pre_y = data.nodes[node]["pos"]
        for _ in range(100):
            x = random.randint(pre_x - distance, pre_x + distance)
            y = random.randint(pre_y - distance, pre_y + distance)
            if x < 0 or y < 0:
                continue
            point = shapely.geometry.Point(x, y)
            if multipoint.intersects(point):
                continue
            return point, (x, y)
        raise No_Solution_Error

    try:
        if distance == -1:
            point, pos = global_move()
        else:
            point, pos = lokal_move(distance)
    except No_Solution_Error:
        logging.error(
            f"Bewege Knoten {node} nicht, da keine Lösung gefunden werden konnte."
        )
        return False

    logging.info(f"Bewege Knoten {node} von {data.nodes[node]['point']} nach {point}")
    data.nodes[node]["point"] = point
    data.nodes[node]["pos"] = pos
    return True

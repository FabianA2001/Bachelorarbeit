from ._cgal_bindings import FieldNumber, Point, Polygon, PolygonWithHoles


def nicht_löschen():
    FieldNumber
    Point
    Polygon
    PolygonWithHoles


def cpp_all_intersection(
    edges: list[tuple[int, int]],
) -> dict[tuple[int, int], set[tuple[int, int]]]:
    return {}

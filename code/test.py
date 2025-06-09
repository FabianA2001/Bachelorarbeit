from shapely import LineString
import random as rd
from itertools import combinations
from shapely.strtree import STRtree
from tqdm import tqdm
import time
import argparse


def sign(x):
    """Return the sign of x as -1 or 1."""
    return (x > 0) - (x < 0)


def orientation(p1, p2, p3):
    """Check if the turn from p1 to p2 to p3 is a left turn."""
    return sign((p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0]))


def calculate_intersections_n2(line_indices, lines, points):
    """
    Naive O(N^2) method to calculate intersections between lines.
    """
    intersections = []
    for (i, ((i1, j1), line1)), (j, ((i2, j2), line2)) in tqdm(
        combinations(enumerate(zip(line_indices, lines)), 2)
    ):
        if i1 == i2 or i1 == j2 or j1 == i2 or j1 == j2:
            continue

        if line1.crosses(line2):
            intersections.append((min(i, j), max(i, j)))

    return intersections


def calculate_intersections_with_str(line_indices, lines, points):
    """
    Attempt to improve intersection tests using an STRtree.
    """
    tree = STRtree(lines)
    intersections = set()
    for i, line in enumerate(lines):
        candidates = tree.query(line)
        for candidate in candidates:
            if i == candidate:
                continue
            if line.crosses(lines[candidate]):
                intersections.add((min(i, candidate), max(i, candidate)))

    return list(intersections)


def calculate_intersections_with_points(line_indices, lines, points):
    """
    Using custom orientation check is more efficient than using
    line2 = line_indices_to_line[(k, l)]
    if line1.crosses(line2):
        line2_idx = line_indices_to_line_idx[(k, l)]
        intersections.append((min(line1_idx, line2_idx), max(line1_idx, line2_idx)))
    """
    intersections = []
    point_indices_to_line_idx = {(i, j): k for k, (i, j) in enumerate(line_indices)}

    for node1_index, node2_index in combinations(range(len(points)), 2):
        line1_idx = point_indices_to_line_idx[(node1_index, node2_index)]

        for index_all_points in range(len(points)):
            if index_all_points == node1_index or index_all_points == node2_index:
                continue

            orientation_node1_node2_index_all = orientation(
                points[node1_index], points[node2_index], points[index_all_points]
            )
            for index_remaining_points in range(index_all_points + 1, len(points)):
                if (
                    index_remaining_points == node1_index
                    or index_remaining_points == node2_index
                    or (node1_index, node2_index)
                    < (index_all_points, index_remaining_points)
                ):
                    continue  # make sure to not double count

                orientation_node1_node2_index_remaining = orientation(
                    points[node1_index],
                    points[node2_index],
                    points[index_remaining_points],
                )

                # both points are on the same side of the line
                if (
                    orientation_node1_node2_index_all
                    == orientation_node1_node2_index_remaining
                ):
                    continue

                orientation_all_remaining_node1 = orientation(
                    points[index_all_points],
                    points[index_remaining_points],
                    points[node1_index],
                )
                orientation_all_remaining_node2 = orientation(
                    points[index_all_points],
                    points[index_remaining_points],
                    points[node2_index],
                )

                # if the orientations are the same, the lines do not intersect
                if orientation_all_remaining_node1 == orientation_all_remaining_node2:
                    continue

                line2_idx = point_indices_to_line_idx[
                    (index_all_points, index_remaining_points)
                ]
                intersections.append(
                    (min(line1_idx, line2_idx), max(line1_idx, line2_idx))
                )

    return intersections


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--n", type=int, default=50, help="Number of points to generate"
    )
    args = parser.parse_args()

    rd.seed(42)
    n = args.n
    points = [(rd.uniform(0, 10), rd.uniform(0, 10)) for _ in range(n)]

    line_indices = list(combinations(range(n), 2))
    lines = [LineString([points[i], points[j]]) for i, j in line_indices]

    print("Naive N^2 method...")
    n2_start = time.time()
    intersections = calculate_intersections_n2(line_indices, lines, points)
    print(
        "N^2 Intersections found:",
        len(intersections),
        "in",
        time.time() - n2_start,
        "seconds",
    )

    print("STR method...")
    str_start = time.time()
    str_intersections = calculate_intersections_with_str(line_indices, lines, points)
    print(
        "STR Intersections found:",
        len(str_intersections),
        "in",
        time.time() - str_start,
        "seconds",
    )

    print("Point method...")
    point_start = time.time()
    point_intersections = calculate_intersections_with_points(
        line_indices, lines, points
    )
    print(
        "Point Intersections found:",
        len(point_intersections),
        "in",
        time.time() - point_start,
        "seconds",
    )

    assert set(intersections) == set(
        str_intersections
    ), "Intersections do not match between N^2 and STR methods"
    assert set(intersections) == set(
        point_intersections
    ), "Intersections do not match between N^2 and point methods"

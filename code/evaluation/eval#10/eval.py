import os
from collections import defaultdict
from dataclasses import asdict

from dc_triangulation import (
    SAT,
    Graph_Wrapper,
    Node,
    SAT_Parameter,
    load_nodes_from_json,
)


def sat_algorithm(nodes):
    graph = Graph_Wrapper(nodes)
    solver = SAT(graph)
    para = SAT_Parameter(
        intersection=True,
        degree_exact=True,
        # fix_hull=True,
        # all_edges=True,
        # exclude_edges=True,
    )
    solution = solver.solve({"timeout": -1, "args": asdict(para)})
    assert solution["success"], "SAT solver did not find a solution"
    return graph.get_all_active_edges()


def analyze_edge_distribution():
    """Analysiert die Kanten längen verteilung für alle Instanztypen."""
    path = os.path.join(os.path.dirname(__file__), "instances")

    # Dictionary um Daten für jeden Instanztyp zu sammeln
    instance_data = defaultdict(list)

    # Lade alle Instanzen und sammle Edges
    for dir_name in os.listdir(path):
        dir_path = os.path.join(path, dir_name)
        if not os.path.isdir(dir_path):
            continue

        print(f"Processing {dir_name}...")

        for file in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file)
            try:
                nodes: list[Node] = load_nodes_from_json(file_path)
                edges = sat_algorithm(nodes)

                instance_data[dir_name].extend(edges)

            except Exception as e:
                print(f"Error loading {file_path}: {e}")

    return instance_data


if __name__ == "__main__":
    pass

import json
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
    cache_file = os.path.join(os.path.dirname(__file__), "edge_cache.json")

    # Lade existierenden Cache falls vorhanden
    cached_data = {}
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                cached_data = json.load(f)
            print(f"Cache geladen mit {len(cached_data)} Einträgen")
        except Exception as e:
            print(f"Fehler beim Laden des Caches: {e}")
            cached_data = {}

    # Dictionary um Daten für jeden Instanztyp zu sammeln
    instance_data = defaultdict(list)
    new_calculations = 0

    # Lade alle Instanzen und sammle Edges
    for dir_name in os.listdir(path):
        dir_path = os.path.join(path, dir_name)
        if not os.path.isdir(dir_path):
            continue

        print(f"Processing {dir_name}...")

        for file in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file)
            cache_key = f"{dir_name}/{file}"

            try:
                # Prüfe ob bereits im Cache vorhanden
                if cache_key in cached_data:
                    print(f"  Verwende gecachte Daten für {file}")
                    edges = cached_data[cache_key]
                else:
                    print(f"  Berechne neue Daten für {file}")
                    nodes: list[Node] = load_nodes_from_json(file_path)
                    edges = sat_algorithm(nodes)

                    # Speichere im Cache
                    cached_data[cache_key] = edges
                    new_calculations += 1

                instance_data[dir_name].extend(edges)

            except Exception as e:
                print(f"Error loading {file_path}: {e}")

    # Speichere aktualisierten Cache
    if new_calculations > 0:
        try:
            with open(cache_file, "w") as f:
                json.dump(cached_data, f, indent=2)
            print(f"Cache aktualisiert mit {new_calculations} neuen Berechnungen")
        except Exception as e:
            print(f"Fehler beim Speichern des Caches: {e}")

    return instance_data


if __name__ == "__main__":
    pass

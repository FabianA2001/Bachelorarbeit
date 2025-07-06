import json
import logging
import os
import random
from dataclasses import asdict

from dc_triangulation import (
    SAT,
    SAT_TRI,
    Delaunay,
    Graph_Wrapper,
    Gurobi,
    Gurobi_Parameter,
    Gurobi_Tri,
    Gurobi_Tri_Parameter,
    Iterative,
    Ortools,
    Ortools_Parameter,
    Random_Adder,
    Raw_Flips,
    SAT_Parameter,
    SAT_Tri_Parameter,
    load_nodes_from_json,
    time_function,
)


def get_solvers():
    return [
        Raw_Flips,
        Delaunay,
        Iterative,
        Ortools,
        SAT,
        Random_Adder,
        SAT_TRI,
        Gurobi_Tri,
        Gurobi,
    ]


def get_parameters():
    return [
        SAT_Parameter,
        Ortools_Parameter,
        SAT_Tri_Parameter,
        Gurobi_Tri_Parameter,
        Gurobi_Parameter,
    ]


time_function

DATA_PATH = os.path.join(os.path.dirname(__file__), "calculated_data.json")


def load_data(
    file_path: str = DATA_PATH,
) -> dict[str, dict[str, list[tuple[int, int]]]]:
    """
    Lädt Daten aus einer JSON-Datei.
    Falls die Datei nicht existiert, wird ein leeres Dictionary zurückgegeben.

    Args:
        file_path: Pfad zur JSON-Datei

    Returns:
        Dictionary mit den geladenen Daten oder leeres Dictionary
    """
    if not os.path.exists(file_path):
        print(f"Datei {file_path} existiert nicht. Starte mit leeren Daten.")
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"Daten erfolgreich aus {file_path} geladen.")
        return data
    except json.JSONDecodeError as e:
        print(f"Fehler beim Laden der JSON-Datei {file_path}: {e}")
        return {}
    except Exception as e:
        print(f"Unerwarteter Fehler beim Laden von {file_path}: {e}")
        return {}


def save_data(
    data: dict[str, dict[str, list[tuple[int, int]]]], file_path: str = DATA_PATH
) -> bool:
    """
    Speichert Daten in einer JSON-Datei.

    Args:
        data: Dictionary mit den zu speichernden Daten
        file_path: Pfad zur JSON-Datei

    Returns:
        True wenn erfolgreich gespeichert, False bei Fehler
    """
    try:
        # Erstelle das Verzeichnis falls es nicht existiert
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Daten erfolgreich in {file_path} gespeichert.")
        return True
    except Exception as e:
        print(f"Fehler beim Speichern in {file_path}: {e}")
        return False


def get_edges(PATH, PERCENT, KEY):
    # Definiere den Pfad zur JSON-Datei

    # Lade bestehende Daten
    data = load_data()

    # Prüfe ob die Berechnung bereits existiert
    if KEY in data:
        # Konvertiere PERCENT zu String für JSON-Schlüssel-Vergleich
        percent_str = str(PERCENT)
        if percent_str in data[KEY]:
            logging.info(
                f"Daten für {KEY} mit {PERCENT} bereits vorhanden. Gebe gespeicherte Liste zurück."
            )
            return data[KEY][percent_str]

    nodes = load_nodes_from_json(PATH)
    graph = Graph_Wrapper(nodes)
    solver = SAT(graph)
    para = SAT_Parameter(
        intersection=True, degree_exact=True, exclude_edges=True, fix_hull=True
    )
    solver.solve({"timeout": -1, "args": asdict(para)})
    all_edges = graph.get_all_edges()
    logging.info(f"Anzahl aller Kanten: {len(all_edges)}")
    num_desiert_edges = int(len(all_edges) * PERCENT)
    logging.info(f"ziel sind {num_desiert_edges} kanten")
    aktive_edges = graph.get_aktive_graph().edges
    not_active_edges = [edge for edge in all_edges if edge not in aktive_edges]
    result = []

    while len(not_active_edges) > 0 and len(result) < num_desiert_edges:
        edge = random.choice(not_active_edges)
        not_active_edges.remove(edge)
        graph2 = Graph_Wrapper(nodes)
        solver2 = SAT(graph2)
        para2 = SAT_Parameter(
            intersection=True,
            degree_atleast=True,
            all_edges=True,
            fix_hull=True,
        )
        solution = solver2.solve(
            {"timeout": -1, "args": asdict(para2), "debug_set_edges": [edge]}
        )
        if not solution["success"]:
            result.append(edge)

    # Speichere die neuen Daten (PERCENT als String-Schlüssel)
    if KEY not in data:
        data[KEY] = {}
    data[KEY][str(PERCENT)] = result

    # Speichere die Daten
    save_data(data)

    return result


if __name__ == "__main__":
    INST = "simple_40"
    FILE = "000_delaunay_flips.json"
    PATH = os.path.join(os.path.dirname(__file__), "instance", INST, FILE)
    KEY = f"{INST}_{FILE}"
    PERCENT = 0.1

    edges = time_function(get_edges)(PATH, PERCENT, KEY)
    logging.info(f"anzahl Kanten: {len(edges)}")
    print(*edges, sep="\n")

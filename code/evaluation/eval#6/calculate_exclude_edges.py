import json
import logging
import os
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
    Run_Algbench,
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
TIMEOUT = 300
path = os.path.join(os.path.dirname(__file__), "instances")


def load_data(
    file_path: str = DATA_PATH,
) -> dict[str, tuple[list, list]]:
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


def save_data(data: dict[str, tuple[list, list]], file_path: str = DATA_PATH) -> bool:
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


def get_edges(PATH, KEY: str):
    # Definiere den Pfad zur JSON-Datei

    # Lade bestehende Daten
    data = load_data()

    # Prüfe ob die Berechnung bereits existiert
    if KEY in data:
        # Konvertiere PERCENT zu String für JSON-Schlüssel-Vergleich
        return data[KEY]

    nodes = load_nodes_from_json(PATH)
    graph = Graph_Wrapper(nodes)
    solver = SAT(graph)
    para = SAT_Parameter(
        intersection=True,
        degree_exact=True,
        exclude_edges=True,
        fix_hull=True,
        solver_name="Gluecard4",
        degree_encoding=9,
    )
    solver.solve({"timeout": -1, "args": asdict(para)})
    all_edges = graph.get_all_edges()
    logging.info(f"Anzahl aller Kanten: {len(all_edges)}")
    aktive_edges = list(graph.get_aktive_graph().edges)
    not_active_edges = [edge for edge in all_edges if edge not in aktive_edges]

    data[KEY] = (aktive_edges, not_active_edges)

    # Speichere die Daten
    save_data(data)
    return (aktive_edges, not_active_edges)


if __name__ == "__main__":
    instances = Run_Algbench.get_instances(path)
    for instance, instance_data in instances.items():
        for file, path in instance_data.items():
            get_edges(path, f"{instance}_{file}")

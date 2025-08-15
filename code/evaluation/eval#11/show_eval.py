import hashlib
import logging
import os
import pickle
from collections import defaultdict
from dataclasses import asdict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dc_triangulation import (
    Graph_Wrapper,
    Ortools,
    Ortools_Parameter,
    Run_Algbench,
    load_nodes_from_json,
)
from scipy.interpolate import interp1d

TIMEOUT = 300
path = os.path.join(os.path.dirname(__file__), "instances")
figure_path = os.path.join(os.path.dirname(__file__), "figures")
function_data_cache_file = os.path.join(
    os.path.dirname(__file__), "function_data_cache.pkl"
)
HOST = ["algra01", "algra02", "algra03", "algra04", "algra05", "algra06"]

# Konfiguriere Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_row_hash(row):
    """Erstellt einen eindeutigen Hash für eine Tabellenzeile basierend auf relevanten Spalten."""
    # Verwende relevante Spalten für den Hash (ohne 'function_data')
    key_columns = ["instance", "file", "solver", "args", "run_number"]
    row_data = {col: row[col] for col in key_columns if col in row.index}
    return hashlib.md5(str(sorted(row_data.items())).encode()).hexdigest()


def load_cached_results():
    """Lädt bereits berechnete Ergebnisse aus der Cache-Datei."""
    if os.path.exists(function_data_cache_file):
        try:
            with open(function_data_cache_file, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            logging.info(f"Fehler beim Laden des Caches: {e}")
            return {}
    return {}


def save_cached_results(cache_data):
    """Speichert berechnete Ergebnisse in der Cache-Datei."""
    try:
        with open(function_data_cache_file, "wb") as f:
            pickle.dump(cache_data, f)
        logging.info(f"Cache gespeichert: {len(cache_data)} Einträge")
    except Exception as e:
        logging.info(f"Fehler beim Speichern des Caches: {e}")


def eval_inst_file(
    table: pd.DataFrame,
) -> dict[str, list[float]]:
    assert not table.empty, (
        "Die Tabelle ist leer. Bitte überprüfen Sie die Eingabedaten."
    )
    assert len(table) == 1, "Die Tabelle sollte genau eine Zeile enthalten."
    solution = table["solution"].iloc[0]
    assert type(solution) is dict
    solve_start = solution.get("start_solve", None)
    assert solve_start is not None, "start_solve fehlt in der Lösung."
    stats: None | list[dict[str, float | list[tuple[int, int]]]] = solution.get(
        "stats", None
    )
    assert stats is not None, "stats fehlen in der Lösung."
    assert type(stats) is list, "stats sollte eine Liste sein."
    nodes = load_nodes_from_json(
        os.path.join(path, table["instance"].iloc[0], f"{table['file'].iloc[0]}.json")
    )
    result = defaultdict(list)
    pre_time = table["pre_time"].iloc[0] if "pre_time" in table.columns else 0
    solve_time = table["runtime"].iloc[0] if "runtime" in table.columns else 0
    last_evaluation = (
        table["evaluation"].iloc[0] if "evaluation" in table.columns else 0
    )
    for value in stats:
        graph = Graph_Wrapper(nodes)
        for edge in value["active_edges"]:
            graph.add_edge(edge[0], edge[1])
        eval = graph.evaluate()
        result["timestamp"].append(value["timestamp"] - solve_start + pre_time)
        result["eval"].append(eval)
        result["objective_value"].append(value["objective_value"])
        result["best_objective_bound"].append(value["best_objective_bound"])

    result["timestamp"].append(solve_time + pre_time)
    result["eval"].append(last_evaluation)
    result["objective_value"].append(result["objective_value"][-1])
    result["best_objective_bound"].append(result["best_objective_bound"][-1])

    return result


def draw_instance(
    table: pd.DataFrame,
) -> None:
    """
    Erstellt ein Liniendiagramm für eine Instanz mit mehreren instance_files.
    """
    plt.figure(figsize=(10, 6))

    # Gruppiere nach solver_args und iteriere
    for solver_args, group_df in table.groupby("solver_args"):
        # Sammle alle function_data für diese solver_args
        value_list = []
        for idx, row in group_df.iterrows():
            if row["function_data"] is not None:
                value_list.append(row["function_data"])

        if not value_list:
            continue

        # Erstelle Interpolationsfunktionen für jede Permutation
        interpolation_functions = []

        for permutation_data in value_list:
            timestamps = np.array(permutation_data["timestamp"])
            evals = np.array(permutation_data["eval"])

            # Erstelle Interpolationsfunktion (linear interpolation)
            if len(timestamps) > 1:  # Mindestens 2 Punkte für Interpolation
                interp_func = interp1d(
                    timestamps,
                    evals,
                    kind="linear",
                    bounds_error=False,
                    fill_value=np.nan,
                )
                interpolation_functions.append(
                    (interp_func, timestamps[0], timestamps[-1])
                )
            else:
                raise ValueError(
                    f"Nicht genügend Datenpunkte für Interpolation: {len(timestamps)}"
                )

        # Erstelle ein gemeinsames Zeitgrid
        if interpolation_functions:
            # Verwende den Überlappungsbereich aller Permutationen
            common_min_time = min(func[1] for func in interpolation_functions)
            common_max_time = max(func[2] for func in interpolation_functions)

            if common_min_time < common_max_time:
                # Erstelle 100 Zeitpunkte im gemeinsamen Bereich
                time_grid = np.linspace(common_min_time, common_max_time, 100)

                # Berechne für jeden Zeitpunkt den Durchschnitt aller Permutationen
                averaged_evals = []
                for time_point in time_grid:
                    eval_values = []
                    for interp_func, min_t, max_t in interpolation_functions:
                        if (
                            min_t <= time_point <= max_t
                        ):  # Nur innerhalb des gültigen Bereichs
                            eval_values.append(interp_func(time_point))

                    if (
                        eval_values
                    ):  # Mindestens eine Permutation hat Daten an diesem Zeitpunkt
                        averaged_evals.append(np.mean(eval_values))
                    else:
                        averaged_evals.append(np.nan)

                # Entferne NaN-Werte
                valid_indices = ~np.isnan(averaged_evals)
                if np.any(valid_indices):
                    plt.plot(
                        time_grid[valid_indices],
                        np.array(averaged_evals)[valid_indices],
                        label=str(solver_args),
                        marker="o",
                        markersize=2,
                        linewidth=2,
                    )
    instanz_file = table["instance_file"].iloc[0]
    plt.xlabel("Zeit")
    plt.ylabel("Wert (0-1)")
    plt.title(f"Instanz: {instanz_file}")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 1)  # Werte sind zwischen 0 und 1

    # Speichere das Diagramm
    instanz_file = instanz_file.replace("/", "_").replace(" ", "_")
    output_path = os.path.join(figure_path, f"{instanz_file}.pdf")
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()  # Schließe die Figur um Speicher zu sparen

    logging.info(
        f"Diagramm für Instanz '{instanz_file}' wurde gespeichert unter: {output_path}"
    )


def eval_table(ri: Run_Algbench):
    table = ri.get_table()
    table = ri.apply_instance(table)
    table = ri.apply_args(table)

    # Lade bereits berechnete Ergebnisse
    cached_results = load_cached_results()

    # Erstelle function_data Spalte
    table["function_data"] = None

    new_calculations = 0
    cache_hits = 0

    for idx, row in table.iterrows():
        row_hash = get_row_hash(row)

        if row_hash in cached_results:
            # Verwende gecachtes Ergebnis
            table.at[idx, "function_data"] = cached_results[row_hash]
            cache_hits += 1
            logging.info(
                f"Cache-Hit für Zeile {idx}: {row.get('instance', 'unknown')}/{row.get('file', 'unknown')}"
            )
        else:
            # Berechne neues Ergebnis
            logging.info(
                f"Berechne neue Zeile {idx}: {row.get('instance', 'unknown')}/{row.get('file', 'unknown')}"
            )
            result = eval_inst_file(pd.DataFrame([row]))
            table.at[idx, "function_data"] = result

            # Speichere im Cache
            cached_results[row_hash] = result
            new_calculations += 1

    # Speichere aktualisierten Cache
    if new_calculations > 0:
        save_cached_results(cached_results)
        logging.info(
            f"Cache aktualisiert: {new_calculations} neue Berechnungen, {cache_hits} Cache-Hits"
        )
    else:
        logging.info(
            f"Alle {cache_hits} Zeilen aus Cache geladen - keine neuen Berechnungen nötig"
        )

    return table


def draw_all_instances(table: pd.DataFrame) -> None:
    """
    Erstellt Diagramme für jede Instanzen in der Tabelle.
    """
    for instance_file, group_df in table.groupby("instance_file"):
        if group_df.empty:
            continue
        # Erstelle ein Diagramm für die Instanz
        draw_instance(group_df)


def gesamt():
    outer_parameter = {
        Ortools: [
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    Ortools_Parameter(
                        intersection=True,
                        all_edges=True,
                        fix_hull=True,
                        evaluation_direction=True,
                        save_state_after_solution=True,
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    Ortools_Parameter(
                        intersection=True,
                        all_edges=True,
                        fix_hull=True,
                        min_max_direction=True,
                        save_state_after_solution=True,
                    )
                ),
            },
        ]
    }

    ri = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        host=HOST,
        ignore_correct=True,
        name="gesamt",
    )
    table = eval_table(ri)
    draw_all_instances(table)


if __name__ == "__main__":
    gesamt()

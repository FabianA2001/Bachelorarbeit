import json
import logging
import os
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

TIMEOUT = 300
path = os.path.join(os.path.dirname(__file__), "instances")
figure_path = os.path.join(os.path.dirname(__file__), "figures")
function_data_cache_file = os.path.join(
    os.path.dirname(__file__), "function_data_cache.json"
)
HOST = ["algra01", "algra02", "algra03", "algra04", "algra05", "algra06"]

# Konfiguriere Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_cache():
    """Lädt den Cache aus der JSON-Datei"""
    if os.path.exists(function_data_cache_file):
        try:
            with open(function_data_cache_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            logging.warning(f"Konnte Cache nicht laden: {function_data_cache_file}")
    return {}


def save_cache(cache):
    """Speichert den Cache in die JSON-Datei"""
    try:
        os.makedirs(os.path.dirname(function_data_cache_file), exist_ok=True)
        with open(function_data_cache_file, "w") as f:
            json.dump(cache, f, indent=2)
        logging.info(f"Cache gespeichert: {function_data_cache_file}")
    except IOError as e:
        logging.error(f"Fehler beim Speichern des Caches: {e}")


def get_cache_key(row):
    """Erstellt einen eindeutigen Cache-Schlüssel für eine Zeile"""
    instance = row.get("instance", "unknown")
    file = row.get("file", "unknown")
    args = str(row.get("solver_args", ""))
    run_number = row.get("run_number", 0)

    return {
        "instance": instance,
        "file": file,
        "args": args,
        "run_number": run_number,
    }


def get_cached_result(cache, cache_key):
    """Holt ein Ergebnis aus dem Cache"""
    try:
        return (
            cache.get(cache_key["instance"], {})
            .get(cache_key["file"], {})
            .get(cache_key["args"], {})
            .get(str(cache_key["run_number"]))
        )
    except (KeyError, TypeError):
        return None


def save_cached_result(cache, cache_key, result):
    """Speichert ein Ergebnis im Cache"""
    instance = cache_key["instance"]
    file = cache_key["file"]
    args = cache_key["args"]
    run_number = str(cache_key["run_number"])

    if instance not in cache:
        cache[instance] = {}
    if file not in cache[instance]:
        cache[instance][file] = {}
    if args not in cache[instance][file]:
        cache[instance][file][args] = {}

    cache[instance][file][args][run_number] = result


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

        # Sammle alle timestamp/eval Paare in einer Liste
        all_data_points = []
        for permutation_data in value_list:
            # Füge alle timestamp/eval Paare zur Liste hinzu
            for timestamp, eval_value in zip(
                permutation_data["timestamp"], permutation_data["eval"]
            ):
                all_data_points.append((timestamp, eval_value))

        # Sortiere alle Datenpunkte nach timestamp
        all_data_points.sort(key=lambda x: x[0])

        assert all_data_points, (
            f"Keine Datenpunkte für solver_args: {solver_args}. "
            "Überprüfen Sie die Eingabedaten."
        )
        max_eval = 0
        monton_all_data_points = []
        for timestamp, eval_value in all_data_points:
            max_eval = max(max_eval, eval_value)
            monton_all_data_points.append((timestamp, max_eval))

        # Extrahiere sortierte timestamps und evals
        if monton_all_data_points:
            sorted_timestamps = np.array([point[0] for point in monton_all_data_points])
            sorted_evals = np.array([point[1] for point in monton_all_data_points])

            # Plotte die sortierten Daten
            plt.plot(
                sorted_timestamps,
                sorted_evals,
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
    # sort
    table = table.sort_values(
        ["instance", "file", "solver_args", "run_number"]
    ).reset_index(drop=True)
    # Lade bereits berechnete Ergebnisse
    cache = load_cache()

    # Erstelle function_data Spalte
    table["function_data"] = None

    new_calculations = 0
    cache_hits = 0

    for idx, row in table.iterrows():
        cache_key = get_cache_key(row)
        cached_result = get_cached_result(cache, cache_key)

        if cached_result is not None:
            # Verwende gecachtes Ergebnis
            table.at[idx, "function_data"] = cached_result
            cache_hits += 1
            logging.info(
                f"Cache-Hit für Zeile {idx}: {cache_key['instance']}/{cache_key['file']} (run: {cache_key['run_number']})"
            )
        else:
            # Berechne neues Ergebnis
            logging.info(
                f"Berechne neue Zeile {idx}: {cache_key['instance']}/{cache_key['file']} (run: {cache_key['run_number']})"
            )
            result = eval_inst_file(pd.DataFrame([row]))
            table.at[idx, "function_data"] = result

            # Speichere im Cache
            save_cached_result(cache, cache_key, result)
            save_cache(cache)  # Speichere nach jeder Berechnung
            new_calculations += 1

    logging.info(
        f"Berechnungen abgeschlossen: {new_calculations} neue, {cache_hits} aus Cache"
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
    # for idx, row in table.iterrows():
    #     draw_instance(pd.DataFrame([row]))


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
    # import streamlit as st
    # st.dataframe(table)

    draw_all_instances(table)


if __name__ == "__main__":
    gesamt()

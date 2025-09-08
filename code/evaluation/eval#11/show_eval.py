import json
import logging
import os
import random
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

# Font-Größen aus Cactus Plot übernommen
TITEL_FONT_SIZE = 20
LABEL_FONT_SIZE = 15
ACHSEN_FONT_SIZE = 12
LEGENDE_FONT_SIZE = 20

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


def draw_all_instances(
    table: pd.DataFrame, table_border: pd.DataFrame, legend_position: str = "right"
) -> None:
    """
    Erstellt Diagramme für jede Instanzen in der Tabelle, gruppiert nach Dateinummer.
    Erstellt für jede Zahl im Dateinamen (z.B. 36, 37, 38, 39) eine separate PDF-Datei
    mit Subplots für jede Instanz.

    Args:
        table: DataFrame mit den Hauptdaten
        table_border: DataFrame mit den Referenzdaten
        legend_position: Position der Legende ("bottom", "right", oder "bottom_right")
    """
    import seaborn as sns

    # Extrahiere Zahlen aus Dateinamen
    table = table.copy()
    table["file_number"] = table["file"].str.extract(r"(\d+)").astype(int)

    # Seaborn Style setzen
    sns.set_style("whitegrid")

    # Gruppiere nach Dateinummer
    for file_number, file_group in table.groupby("file_number"):
        if file_group.empty:
            continue

        # Bestimme eindeutige Instanzen für diese Dateinummer
        unique_instances = file_group["instance"].unique()
        n_instances = len(unique_instances)

        if n_instances == 0:
            continue

        # Bestimme Layout für Subplots
        cols = min(3, n_instances)  # Maximal 3 Spalten
        rows = (n_instances + cols - 1) // cols  # Aufrunden

        fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows))

        # Für den Fall dass nur eine Instanz vorhanden ist
        if n_instances == 1:
            axes = [axes]
        elif rows == 1:
            axes = axes if isinstance(axes, (list, np.ndarray)) else [axes]
        else:
            axes = axes.flatten()

        # Für jede Instanz einen eigenen Subplot
        for idx, instance in enumerate(unique_instances):
            ax = axes[idx]

            # Filtere Daten für diese Instanz und Dateinummer
            instance_data = file_group[file_group["instance"] == instance]

            # Filtere table_border nach Instanz und file_number
            border_rows = table_border[table_border["instance"] == instance]
            found = False
            if not border_rows.empty:
                border_row = border_rows[
                    border_rows["file"].str.contains(str(file_number), na=False)
                ]
                if not border_row.empty:
                    assert len(border_row) == 1, (
                        f"Es sollte genau eine Zeile für Instanz '{instance}' und Dateinummer '{file_number}' geben."
                    )
                    found = True
                    border_row = border_row.iloc[0]
                    border_timestamp = border_row["runtime"] + border_row["pre_time"]

                    # Füge Referenz-Solver hinzu (von (0,0) zu (border_timestamp, 100) zu (timeout, 100))
                    reference_timestamps = [
                        0,
                        border_timestamp,
                        border_timestamp,
                        TIMEOUT,
                    ]
                    reference_evals = [
                        0,
                        0,
                        100,
                        100,
                    ]  # Multipliziert mit 100 für Prozent
            if not found:
                reference_timestamps = [0, TIMEOUT]
                reference_evals = [0, 0]  # Multipliziert mit 100 für Prozent

            ax.plot(
                reference_timestamps,
                reference_evals,
                label="Referenz",
                color="green",
                linestyle="-",
                linewidth=2,
                alpha=0.8,
            )

            # Gruppiere nach solver_args und plotte
            for solver_args, group_df in instance_data.groupby("solver_args"):
                # Sammle alle function_data für diese solver_args
                value_list = []
                for _, row in group_df.iterrows():
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

                if not all_data_points:
                    continue

                max_eval = 0
                monton_all_data_points = []
                for timestamp, eval_value in all_data_points:
                    max_eval = max(max_eval, eval_value)
                    monton_all_data_points.append((timestamp, max_eval))

                # Extrahiere sortierte timestamps und evals
                if monton_all_data_points:
                    sorted_timestamps = np.array(
                        [point[0] for point in monton_all_data_points]
                    )
                    sorted_evals = np.array(
                        [point[1] for point in monton_all_data_points]
                    )

                    # Füge einen Punkt beim Timeout hinzu, falls der letzte Punkt vor dem Timeout liegt
                    if len(sorted_timestamps) > 0 and sorted_timestamps[-1] < TIMEOUT:
                        # Aktueller letzter Wert bleibt beim Timeout bestehen
                        sorted_timestamps = np.concatenate(
                            [sorted_timestamps, [TIMEOUT]]
                        )
                        sorted_evals = np.concatenate(
                            [sorted_evals, [sorted_evals[-1]]]
                        )

                    # Plotte die sortierten Daten (Y-Werte mit 100 multiplizieren für Prozent)
                    ax.plot(
                        sorted_timestamps,
                        sorted_evals * 100,
                        label=str(solver_args),
                        marker="o",
                        markersize=2,
                        linewidth=2,
                    )

            # Subplot Styling
            ax.set_xlabel("Zeit (Sekunden)", fontsize=LABEL_FONT_SIZE)
            ax.set_ylabel("Wert (%)", fontsize=LABEL_FONT_SIZE)

            # Titel für die Instanz
            instance_titel = instance
            if instance == "greedy":
                instance_titel = "Greedy"
            elif instance == "delaunay":
                instance_titel = "Delaunay"
            elif instance == "iterative":
                instance_titel = "Iterative"
            elif instance == "random":
                instance_titel = "Random"
            elif instance == "d_flips":
                instance_titel = "Delaunay-Flips"

            ax.set_title(instance_titel, fontsize=TITEL_FONT_SIZE, fontweight="bold")
            ax.grid(True, alpha=0.3, linestyle="-", linewidth=0.5)
            ax.set_ylim(0, 105)  # Werte sind zwischen 0 und 100%, mit etwas Platz oben
            ax.set_xlim(0, TIMEOUT + 25)  # Platz für Timeout-Linie und Beschriftung

            # Schriftgröße der Achsen-Zahlen anpassen
            ax.tick_params(axis="both", which="major", labelsize=ACHSEN_FONT_SIZE)

            # Horizontale Linie bei 100% hinzufügen
            ax.axhline(
                y=100,
                color="red",
                linestyle="--",
                alpha=0.6,
                linewidth=1.5,
            )

            # Vertikale Linie bei Timeout hinzufügen
            ax.axvline(
                x=TIMEOUT,
                color="red",
                linestyle="--",
                alpha=0.7,
                linewidth=1.5,
            )

            # Beschriftung für die Timeout-Linie
            ax.text(
                TIMEOUT + 10,
                52.5,  # Mitte der Y-Achse (0-105% / 2)
                f"Timeout ({TIMEOUT}s)",
                rotation=90,
                verticalalignment="center",
                horizontalalignment="left",
                fontsize=ACHSEN_FONT_SIZE,
                color="red",
                alpha=0.8,
            )

        # Verstecke überschüssige Subplots
        for idx in range(n_instances, len(axes)):
            axes[idx].set_visible(False)

        # Entferne Legenden von allen Subplots
        for ax in axes[:n_instances]:
            if ax.get_legend():
                ax.get_legend().remove()

        handel_names = {
            "Ortools-1": "Durchschnitt",
            "Ortools-2": "Min-Max",
            "Referenz": "Referenz",
        }

        # Eine gemeinsame Legende für die gesamte Figur
        if n_instances > 0:
            handles, labels = axes[0].get_legend_handles_labels()
            if handles:
                # Update labels mit benutzerdefinierten Namen
                updated_labels = []
                for label in labels:
                    updated_labels.append(handel_names.get(label, label))

                if legend_position == "right":
                    fig.legend(
                        handles,
                        updated_labels,
                        loc="center left",
                        bbox_to_anchor=(1.0, 0.5),
                        fontsize=LEGENDE_FONT_SIZE,
                        frameon=True,
                        fancybox=True,
                        shadow=True,
                    )
                elif legend_position == "bottom_right":
                    fig.legend(
                        handles,
                        updated_labels,
                        loc="lower right",
                        bbox_to_anchor=(0.935, 0.11),
                        fontsize=LEGENDE_FONT_SIZE,
                        frameon=True,
                        fancybox=True,
                        shadow=True,
                        bbox_transform=fig.transFigure,
                    )
                else:  # bottom (default)
                    fig.legend(
                        handles,
                        updated_labels,
                        loc="upper center",
                        bbox_to_anchor=(0.5, 0.0),
                        ncol=min(3, len(handles)),  # Maximal 3 Einträge pro Zeile
                        fontsize=LEGENDE_FONT_SIZE,
                        frameon=True,
                        fancybox=True,
                        shadow=True,
                    )

        # Layout optimieren
        fig.tight_layout()

        # Speichere das Diagramm mit Dateinummer
        output_path = os.path.join(figure_path, f"eval_progression_{file_number}.pdf")
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()  # Schließe die Figur um Speicher zu sparen

        logging.info(
            f"Diagramm für Dateinummer '{file_number}' wurde gespeichert unter: {output_path}"
        )


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
    return table


def border():
    outer_parameter = {
        Ortools: [
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    Ortools_Parameter(
                        intersection=True,
                        degree=True,
                        all_edges=True,
                        fix_hull=True,
                    )
                ),
            }
        ]
    }
    ri = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        host=HOST,
        name="gesamt",
    )
    table = ri.get_table()
    table = ri.apply_instance(table)
    table = ri.apply_args(table)
    table = ri.get_mean(table)
    # import streamlit as st
    # st.dataframe(table)
    return table


def print_inst():
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
    table = ri.get_table()
    table = ri.apply_instance(table)
    table = ri.apply_args(table)
    table = table.iloc[0]

    stats: None | list[dict[str, float | list[tuple[int, int]]]] = table[
        "solution"
    ].get("stats", None)
    assert stats is not None, "stats fehlen in der Lösung."
    assert table["run_seed"] != 0, "run_seed fehlt in der Lösung."
    seed = table["run_seed"]
    stat = stats[-1]
    nodes = load_nodes_from_json(
        os.path.join(path, table["instance"], f"{table['file']}.json")
    )
    random.seed(seed)
    random.shuffle(nodes)
    graph = Graph_Wrapper(nodes)
    for edge in stat["active_edges"]:
        graph.add_edge(edge[0], edge[1])
    graph.show_and_save(save=".", draw_name=False)


if __name__ == "__main__":
    # table = gesamt()
    # table_2 = border()
    # # # Standardmäßig Legende unten, aber kann geändert werden zu "right"
    # draw_all_instances(table, table_2, legend_position="bottom_right")
    print_inst()

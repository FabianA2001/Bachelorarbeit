import os
from collections import defaultdict
from dataclasses import asdict

import matplotlib.pyplot as plt
import pandas as pd
from dc_triangulation import (
    Graph_Wrapper,
    Ortools,
    Ortools_Parameter,
    Run_Algbench,
    load_nodes_from_json,
    time_function,
)

TIMEOUT = 80
path = os.path.join(os.path.dirname(__file__), "instances")
figure_path = os.path.join(os.path.dirname(__file__), "figures")
HOST = ["algry01", "algry02", "algry03", "algry04"]


def eval_inst_file(
    table: pd.DataFrame,
) -> list[dict[str, float | list[tuple[int, int]]]]:
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
    for value in stats:
        graph = Graph_Wrapper(nodes)
        for edge in value["active_edges"]:
            graph.add_edge(edge[0], edge[1])
        eval = graph.evaluate()
        # graph.name = table["instance_file"].iloc[0]
        # graph.show_and_save(show=False, save=figure_path)
        value["start_time"] = value["timestamp"] - solve_start
        value["eval"] = eval
    return stats


def draw_instance(
    instanz: str, data: list[tuple[str, list[dict[str, float | list[tuple[int, int]]]]]]
) -> None:
    """
    Erstellt ein Liniendiagramm für eine Instanz mit mehreren instance_files.

    Args:
        instanz: Name der Instanz
        data: Liste von Tupeln (instance_file, [(zeitpunkt, wert)])
    """
    plt.figure(figsize=(10, 6))

    for instance_file, value in data:
        if value:  # Nur plotten wenn Daten vorhanden sind
            times = []
            values = []
            for entry in value:
                times.append(entry["start_time"])
                values.append(entry["eval"])
            plt.plot(times, values, label=instance_file, marker="o")

    plt.xlabel("Zeit")
    plt.ylabel("Wert (0-1)")
    plt.title(f"Instanz: {instanz}")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 1)  # Werte sind zwischen 0 und 1

    # Speichere das Diagramm
    output_path = os.path.join(figure_path, f"{instanz}.pdf")
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()  # Schließe die Figur um Speicher zu sparen

    print(f"Diagramm für Instanz '{instanz}' wurde gespeichert unter: {output_path}")


def eval_table(ri: Run_Algbench):
    table = ri.get_table()
    table = ri.apply_instance(table)
    table = ri.apply_args(table)
    inst_to_data = defaultdict(list)
    # rufe für jede Instanz eval_inst_file auf
    for instance_file in table["instance_file"].unique():
        instance_table = table[table["instance_file"] == instance_file]
        assert not instance_table.empty, (
            "Die Tabelle ist leer. Bitte überprüfen Sie die Eingabedaten."
        )
        assert len(instance_table) == 1, (
            f"Die Tabelle sollte genau eine Zeile enthalten.\n{instance_table}"
        )
        inst_to_data[instance_table["instance"].iloc[0]].append(
            (
                instance_table["file"].iloc[0],
                time_function(eval_inst_file)(instance_table),
            )
        )

    for instance, data in inst_to_data.items():
        draw_instance(instance, data)


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
        ]
    }

    ri = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        # host=HOST,
        name="gesamt",
    )
    eval_table(ri)


if __name__ == "__main__":
    gesamt()

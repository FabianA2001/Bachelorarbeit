import os
from dataclasses import asdict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import slurminade
from dc_triangulation import (
    SAT,
    Gurobi,
    Gurobi_Parameter,
    Ortools,
    Ortools_Parameter,
    Run_Algbench,
    SAT_Parameter,
)

TIMEOUT = 300
path = os.path.join(os.path.dirname(__file__), "instances")
benchmark_path = os.path.join(os.path.dirname(__file__), "lokal_benchmark")
# This is the entry point for the evaluation script
# It will run the Run_Instance class from run_algbench module
outer_parameter = {
    SAT: [
        {
            "timeout": TIMEOUT,
            "args": asdict(
                SAT_Parameter(
                    intersection=True,
                    degree_exact=True,
                )
            ),
        },
    ],
    Gurobi: [
        {
            "timeout": TIMEOUT,
            "args": asdict(
                Gurobi_Parameter(
                    intersection=True,
                    degree=True,
                )
            ),
        },
    ],
    Ortools: [
        {
            "timeout": TIMEOUT,
            "args": asdict(
                Ortools_Parameter(
                    intersection=True,
                    degree=True,
                )
            ),
        },
    ],
}
RI = Run_Algbench(
    inst_path=path,
    outer_parameter=outer_parameter,
    figure_path=os.path.dirname(__file__),
    host=["algry01", "algry02", "algry03", "algry04"],
    name="permutation",
    path_benchmark=benchmark_path,
)


@slurminade.slurmify()
def run_solver_on_inst(key: str):
    RI.add_entrys(key)


@slurminade.slurmify(mail_type="ALL")
def compress_results():
    # Compress the results to save significant disk space
    RI.compress()


def create_cactus(
    table: pd.DataFrame, y: str, block: bool = True, timelimit: int = 300
):
    """
    Erstellt einen Cactus Plot für die Benchmark-Daten nach Instanzen gruppiert.
    In einem Cactus Plot wird die Zeit (y-Achse) gegen die Anzahl der gelösten
    Instanzen (x-Achse) dargestellt, sortiert nach Laufzeit.
    """
    # Seaborn Style setzen
    sns.set_style("whitegrid")

    # Figure und Axis erstellen
    fig, ax = plt.subplots(figsize=(10, 6))

    # Filter gültige Werte (entferne negative Werte wie -1 für Timeouts)
    valid_data = table[table[y] >= 0].copy()

    if len(valid_data) == 0:
        print(f"Keine gültigen Daten für {y} Cactus Plot gefunden")
        return

    # Eindeutige Instanzen ermitteln
    unique_instances = valid_data["instance"].unique()

    # Bessere Farbpalette für Instanzen - verschiedene Optionen je nach Anzahl
    n_instances = len(unique_instances)

    if n_instances <= 8:
        colors = sns.color_palette("Dark2", n_instances)
    elif n_instances <= 10:
        colors = sns.color_palette("tab10", n_instances)
    elif n_instances <= 12:
        colors = sns.color_palette("Set3", n_instances)
    elif n_instances <= 20:
        colors = sns.color_palette("tab20", n_instances)
    else:
        colors = sns.color_palette("husl", n_instances)

    # Für jede Instanz eine Linie plotten
    for i, instance_label in enumerate(unique_instances):
        # Extrahiere den ursprünglichen Instanznamen (ohne Nummer)
        instance = instance_label.split("-")[0]
        instance_data = valid_data[valid_data["instance"] == instance_label][y].values

        if len(instance_data) == 0:
            continue

        # Gesamtanzahl der Instanzen für diese Kategorie
        total_instances = len(instance_data)

        # Sortieren für Cactus Plot (wichtig!)
        times_sorted = np.sort(instance_data)
        x_values = np.arange(1, len(times_sorted) + 1)

        # Punkt (0,0) hinzufügen - bei Zeit 0 sind 0 Instanzen gelöst
        times_with_zero = np.concatenate([[0], times_sorted])
        x_values_with_zero = np.concatenate([[0], x_values])

        # Y-Werte in Prozent umwandeln
        y_values_percent = (x_values_with_zero / total_instances) * 100

        # Füge einen Punkt beim Timelimit hinzu, falls die Linie nicht bis dahin reicht
        if len(times_with_zero) > 1 and times_with_zero[-1] < timelimit:
            times_with_timelimit = np.concatenate([times_with_zero, [timelimit]])
            y_values_with_timelimit = np.concatenate(
                [y_values_percent, [y_values_percent[-1]]]
            )
        else:
            times_with_timelimit = times_with_zero
            y_values_with_timelimit = y_values_percent

        ax.plot(
            times_with_timelimit,
            y_values_with_timelimit,
            "o-",
            color=colors[i],
            label=instance,
            linewidth=2,
            markersize=3,
            alpha=0.8,
            drawstyle="steps-post",
        )

    # Achsenbeschriftungen und Titel
    ax.set_xlabel(f"{y} (Sekunden)")
    ax.set_ylabel("Gelöste Instanzen (%)")
    ax.set_title(f"Cactus Plot - {y}")

    # Y-Achse auf 0-105% setzen, damit 100%-Linie und Beschriftung sichtbar sind
    ax.set_ylim(0, 105)

    # Horizontale Linie bei 100% hinzufügen
    ax.axhline(y=100, color="green", linestyle="-", alpha=0.8, linewidth=2)

    # Vertikale Linie bei timelimit hinzufügen
    ax.axvline(
        x=timelimit,
        color="red",
        linestyle="--",
        alpha=0.7,
        linewidth=1.5,
    )

    # Legende hinzufügen
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

    # Grid
    ax.grid(True, alpha=0.3)

    # Layout optimieren
    fig.tight_layout()

    # Speichern falls RI verfügbar ist
    try:
        fig_name = RI.name if hasattr(RI, "name") and RI.name else f"cactus_{y}"
        if hasattr(RI, "figure_path") and RI.figure_path:
            fig.savefig(
                os.path.join(RI.figure_path, f"{fig_name}.pdf"),
                dpi=300,
                bbox_inches="tight",
            )
    except Exception:
        # Falls RI nicht verfügbar ist, einfach als cactus_{y}.pdf speichern
        fig.savefig(f"cactus_{y}.pdf", dpi=300, bbox_inches="tight")

    plt.show(block=block)


def lokal_show():
    table = RI.get_table()
    table["total_runtime"] = table["pre_time"] + table["runtime"]
    table = table.sort_values(by=["instance"])
    # table = sort_by_inst(table)

    create_cactus(
        table=table,
        y="total_runtime",
        block=True,
        timelimit=300,
    )


if __name__ == "__main__":
    if True:
        slurminade.update_default_configuration(
            # Your supervisor will tell you these details
            partition="alg",  # Which partition to use. Usually group name.
            constraint="alggen03",  # Which workstations within the partition to use
            exclusive=True,  # To use all cores on a node exclusively
            mail_type="FAIL",  # Send mail on failure
            mail_user="f.alich@tu-braunschweig.de",  # Mail to this address
        )
        run_list = RI.get_run_list()
        with slurminade.JobBundling(max_size=5):
            for key in run_list:
                run_solver_on_inst.distribute(key)

        slurminade.join()
        compress_results.distribute()
    else:
        lokal_show()

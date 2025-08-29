import os
import re
from dataclasses import asdict

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import slurminade
from dc_triangulation import (
    Ortools,
    Ortools_Parameter,
    Run_Algbench,
)

# Font-Konstanten aus show_eval
TITEL_FONT_SIZE = 35
LABEL_FONT_SIZE = 26
ACHSEN_FONT_SIZE = 20
LEGENDE_FONT_SIZE = 30

TIMEOUT = 1800  # 30 minutes in seconds
# path = os.path.join(os.path.dirname(__file__), "instances")
path = os.path.join(os.path.dirname(__file__), "instances_copy")
# This is the entry point for the evaluation script
# It will run the Run_Instance class from run_algbench module
outer_parameter = {
    Ortools: [
        {
            "timeout": TIMEOUT,
            "args": asdict(
                Ortools_Parameter(
                    intersection=True,
                    degree=True,
                    fix_hull=True,
                    all_edges=True,
                    fix_edges=True,
                )
            ),
        },
    ],
}

RI = Run_Algbench(
    inst_path=path,
    outer_parameter=outer_parameter,
    figure_path=os.path.dirname(__file__),
    host=["algra01", "algra02", "algra03", "algra04", "algra05", "algra06"],
    name="Eval15",
)


@slurminade.slurmify()
def run_solver_on_inst(key: str):
    RI.add_entrys(key)


@slurminade.slurmify(mail_type="ALL")
def compress_results():
    # Compress the results to save significant disk space
    RI.compress()


def lokal_show_balken():
    table = RI.get_table()
    table = RI.apply_instance(table)
    table = RI.apply_args(table)
    table = RI.get_mean(table)

    # Vorbereitung der Daten für das Multi-Säulen-Diagramm
    plot_data = []

    grouped = table.groupby("instance")
    for instance_name, instance_group in grouped:
        for index, row in instance_group.iterrows():
            # Runtime extrahieren (in Sekunden)
            runtime = row.get("runtime", 0) + row.get("pre_time", 0)
            if runtime <= 0:
                continue  # Skip if runtime is not valid

            file = row["file"]

            # Extrahiere die Knotenzahl aus dem Dateinamen (zweite Zahl)
            # Suche nach Zahlen im Dateinamen
            numbers = re.findall(r"\d+", file)
            node_number = int(numbers[0]) if len(numbers) > 1 else 0
            node_name = int(numbers[1]) if len(numbers) > 1 else 0

            # Bestimme die Operation basierend auf dem Dateinamen
            operation = ""
            if "move" in file.lower():
                operation = "_move"
            elif "change" in file.lower():
                operation = "_change"
            # Für normale Instanzen bleibt operation leer ("")

            # Erstelle X-Achsen-Label: "Knotenzahl" + Operation
            x_label = f"{node_name}{operation}"
            x = f"{node_number}"

            plot_data.append(
                {
                    "instance": str(instance_name),
                    "file": file,
                    "node_number": node_number,
                    "operation": operation,
                    "x": str(node_number),
                    "x_label": x_label,
                    "runtime": runtime,
                }
            )

    if not plot_data:
        print("Keine gültigen Daten zum Plotten gefunden!")
        return

    # DataFrame für Plotting erstellen
    df_plot = pd.DataFrame(plot_data)

    # Seaborn Style setzen
    sns.set_style("whitegrid")
    plt.figure(figsize=(16, 10))

    # Multi-Säulen-Diagramm erstellen
    sns.barplot(
        data=df_plot,
        x="x",
        y="runtime",
        hue="instance",
        ci=None,  # Keine Konfidenzintervalle
        palette="Set2",
    )

    # Diagramm anpassen
    plt.xlabel("Knotenzahl und Operation", fontsize=LABEL_FONT_SIZE)
    plt.ylabel("Laufzeit (Sekunden)", fontsize=LABEL_FONT_SIZE)

    # Natürliche Sortierung für X-Achsen-Labels
    def natural_sort_key(text):
        return [
            int(x) if x.isdigit() else x.lower() for x in re.split(r"([0-9]+)", text)
        ]

    # Erstelle Custom X-Tick Labels ohne die erste Nummer
    unique_x_labels = sorted(df_plot["x"].unique(), key=natural_sort_key)
    unique_display_labels = []
    for x_label in unique_x_labels:
        # Finde das entsprechende display_label für dieses x_label
        display_label = df_plot[df_plot["x"] == x_label]["x_label"].iloc[0]
        unique_display_labels.append(display_label)

    plt.xticks(
        range(len(unique_x_labels)), unique_display_labels, rotation=45, ha="right"
    )

    # Legende anpassen
    plt.legend(
        title="Instanz",
        bbox_to_anchor=(0.5, -0.25),
        loc="upper center",
        fontsize=LEGENDE_FONT_SIZE,
        ncol=3,
        title_fontsize=LEGENDE_FONT_SIZE,
    )

    # Achsen-Tick-Größen anpassen
    plt.gca().tick_params(axis="both", which="major", labelsize=ACHSEN_FONT_SIZE)

    # Layout anpassen
    plt.tight_layout()

    # Diagramm speichern
    output_path = os.path.join(os.path.dirname(__file__), "eval15.pdf")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")

    # Diagramm anzeigen
    plt.show()


def lokal_show_kaktus():
    table = RI.get_table()
    table = RI.apply_instance(table)
    table = RI.apply_args(table)
    table = RI.get_mean(table)

    # Vorbereitung der Daten für das Kaktusdiagramm
    plot_data = []

    grouped = table.groupby("instance")
    for instance_name, instance_group in grouped:
        instance_runtimes = []

        for index, row in instance_group.iterrows():
            # Runtime extrahieren (in Sekunden)
            runtime = row.get("runtime", 0) + row.get("pre_time", 0)
            if runtime <= 0 or runtime > TIMEOUT:
                continue  # Skip if runtime is not valid or timeout

            file = row["file"]
            numbers = re.findall(r"\d+", file)
            node_number = int(numbers[0]) if len(numbers) > 1 else 0
            node_name = int(numbers[1]) if len(numbers) > 1 else 0
            # Berechne die Knotenzahl: Start bei 80, nach jeder 4. Lösung +10
            # Bei 1-4 Lösungen: 80 Knoten, bei 5-8: 90 Knoten, bei 9-12: 100 Knoten, etc.

            plot_data.append(
                {
                    "instance": str(instance_name),
                    "runtime": runtime,
                    "node_count": node_name,  # Knotenzahl für X-Achse
                }
            )

    if not plot_data:
        print("Keine gültigen Daten zum Plotten gefunden!")
        return
    # DataFrame für Plotting erstellen
    df_plot = pd.DataFrame(plot_data)
    df_plot = df_plot.loc[
        df_plot.groupby(["instance", "node_count"])["runtime"].idxmin()
    ]

    # Seaborn Style setzen
    sns.set_style("whitegrid")
    plt.figure(figsize=(16, 10))

    # Kaktusdiagramm erstellen - jede Instanz als separate Linie
    instances = df_plot["instance"].unique()
    colors = sns.color_palette("Set2", len(instances))

    for i, instance in enumerate(instances):
        instance_data = df_plot[df_plot["instance"] == instance]

        # Sortiere nach Laufzeit für eine saubere Linie
        instance_data = instance_data.sort_values("runtime")

        # Entferne Einträge wo es vorher schon bessere Knotenzahlen gab (für monoton steigende Kurve)
        filtered_data = []
        max_node_count = 0

        for _, row in instance_data.iterrows():
            if row["node_count"] > max_node_count:
                max_node_count = row["node_count"]
                filtered_data.append(row)

        if not filtered_data:
            continue

        instance_data = pd.DataFrame(filtered_data)

        inst_name = "Default"
        if instance == "d_flips":
            inst_name = "Delaunay-Flips"
        elif instance == "greedy":
            inst_name = "Greedy"
        elif instance == "delaunay":
            inst_name = "Delaunay"
        elif instance == "random":
            inst_name = "Random"
        elif instance == "iterative":
            inst_name = "Iterative"

        plt.plot(
            instance_data["runtime"],
            instance_data["node_count"],
            label=inst_name,
            color=colors[i],
            linewidth=2.5,
            marker="o",
            markersize=4,
            drawstyle="steps-post",
        )

        # Erweitere die Linie horizontal bis zum Timeout
        if len(instance_data) > 0:
            last_runtime = instance_data["runtime"].iloc[-1]
            last_node_count = instance_data["node_count"].iloc[-1]
            if last_runtime < TIMEOUT:
                # Zeichne horizontale Linie vom letzten Punkt bis zum Timeout
                plt.plot(
                    [last_runtime, TIMEOUT],
                    [last_node_count, last_node_count],
                    color=colors[i],
                    linewidth=2.5,
                    linestyle="-",
                    alpha=0.7,
                )

    # Diagramm anpassen
    plt.xlabel("Laufzeit (Sekunden)", fontsize=LABEL_FONT_SIZE)
    plt.ylabel("Knotenzahl", fontsize=LABEL_FONT_SIZE)
    # plt.title("Kaktusdiagramm - Knotenzahl über Zeit", fontsize=TITEL_FONT_SIZE)

    # Timeout-Linie hinzufügen
    plt.axvline(x=TIMEOUT, color="red", linestyle="--", linewidth=2, alpha=0.7)

    # Timeout-Text hinzufügen (wie in run_algbench)
    plt.text(
        TIMEOUT + 80,
        130,
        f"Timeout ({TIMEOUT}s)",
        rotation=90,
        verticalalignment="center",
        horizontalalignment="right",
        fontsize=ACHSEN_FONT_SIZE,
        color="red",
        alpha=0.8,
    )

    # Legende anpassen
    plt.legend(
        title="Instanz",
        bbox_to_anchor=(1.05, 1),
        loc="upper left",
        fontsize=LEGENDE_FONT_SIZE,
        title_fontsize=LEGENDE_FONT_SIZE,
    )

    # Achsen-Tick-Größen anpassen
    plt.gca().tick_params(axis="both", which="major", labelsize=ACHSEN_FONT_SIZE)

    # Grid für bessere Lesbarkeit
    plt.grid(True, alpha=0.3)

    # Layout anpassen
    plt.tight_layout()

    # Diagramm speichern
    output_path = os.path.join(os.path.dirname(__file__), "kaktus_eval15.pdf")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")

    # Diagramm anzeigen
    plt.show()


def lokal_show_ja_nein():
    table = RI.get_table()
    table = RI.apply_instance(table)
    table = RI.apply_args(table)
    table = RI.get_mean(table)

    table["nein_instanze"] = table["file"].apply(
        lambda x: True if "change" in x.lower() or "move" in x.lower() else False
    )

    # Vorbereitung der Daten für das Kaktusdiagramm
    plot_data = []

    # Gruppiere nach nein_instanze (True/False) anstatt nach instance
    grouped = table.groupby("nein_instanze")
    for is_nein_instanze, group in grouped:
        instance_runtimes = []

        for index, row in group.iterrows():
            # Runtime extrahieren (in Sekunden)
            runtime = row.get("runtime", 0) + row.get("pre_time", 0)
            if runtime <= 0 or runtime > TIMEOUT:
                continue  # Skip if runtime is not valid or timeout

            instance_runtimes.append(runtime)
            file = row["file"]
            numbers = re.findall(r"\d+", file)
            node_number = int(numbers[0]) if len(numbers) > 1 else 0
            node_name = int(numbers[1]) if len(numbers) > 1 else 0

            # Erstelle Labels für die Gruppierung
            group_label = "Nein-Instanzen" if is_nein_instanze else "Ja-Instanzen"

            plot_data.append(
                {
                    "group": group_label,
                    "runtime": runtime,
                    "node_count": node_name,  # Knotenzahl für Y-Achse
                    "is_nein": is_nein_instanze,
                }
            )

    if not plot_data:
        print("Keine gültigen Daten zum Plotten gefunden!")
        return

    plot_data.sort(key=lambda x: x["runtime"])

    # DataFrame für Plotting erstellen
    df_plot = pd.DataFrame(plot_data)
    df_plot = df_plot.loc[
        df_plot.groupby(["node_count", "is_nein"])["runtime"].idxmin()
    ]

    # Seaborn Style setzen
    sns.set_style("whitegrid")
    plt.figure(figsize=(16, 10))

    # Kaktusdiagramm erstellen - jede Gruppe (Ja/Nein) als separate Linie
    groups = df_plot["group"].unique()
    colors = ["green", "red"]  # Grün für Ja-Instanzen, Rot für Nein-Instanzen

    for i, group in enumerate(groups):
        group_data = df_plot[df_plot["group"] == group]

        # Sortiere nach Laufzeit für eine saubere Linie
        group_data = group_data.sort_values("runtime")

        # Entferne Einträge wo es vorher schon bessere Knotenzahlen gab (für monoton steigende Kurve)
        filtered_data = []
        max_node_count = 0

        for _, row in group_data.iterrows():
            if row["node_count"] > max_node_count:
                max_node_count = row["node_count"]
                filtered_data.append(row)

        if not filtered_data:
            continue

        group_data = pd.DataFrame(filtered_data)

        plt.plot(
            group_data["runtime"],
            group_data["node_count"],
            label=group,
            color=colors[i],
            linewidth=2.5,
            marker="o",
            markersize=4,
            drawstyle="steps-post",
        )

        # Erweitere die Linie horizontal bis zum Timeout
        if len(group_data) > 0:
            last_runtime = group_data["runtime"].iloc[-1]
            last_node_count = group_data["node_count"].iloc[-1]
            if last_runtime < TIMEOUT:
                # Zeichne horizontale Linie vom letzten Punkt bis zum Timeout
                plt.plot(
                    [last_runtime, TIMEOUT],
                    [last_node_count, last_node_count],
                    color=colors[i],
                    linewidth=2.5,
                    linestyle="-",
                    alpha=0.7,
                )

    # Diagramm anpassen
    plt.xlabel("Laufzeit (Sekunden)", fontsize=LABEL_FONT_SIZE)
    plt.ylabel("Knotenzahl", fontsize=LABEL_FONT_SIZE)
    # plt.title("Kaktusdiagramm - Ja/Nein Instanzen", fontsize=TITEL_FONT_SIZE)

    # Timeout-Linie hinzufügen
    plt.axvline(x=TIMEOUT, color="red", linestyle="--", linewidth=2, alpha=0.7)

    # Timeout-Text hinzufügen
    plt.text(
        TIMEOUT + 80,
        120,
        f"Timeout ({TIMEOUT}s)",
        rotation=90,
        verticalalignment="center",
        horizontalalignment="right",
        fontsize=ACHSEN_FONT_SIZE,
        color="red",
        alpha=0.8,
    )

    # Legende anpassen
    plt.legend(
        title="Instanz-Typ",
        bbox_to_anchor=(1.05, 1),
        loc="upper left",
        fontsize=LEGENDE_FONT_SIZE,
        title_fontsize=LEGENDE_FONT_SIZE,
    )

    # Achsen-Tick-Größen anpassen
    plt.gca().tick_params(axis="both", which="major", labelsize=ACHSEN_FONT_SIZE)

    # Grid für bessere Lesbarkeit
    plt.grid(True, alpha=0.3)

    # Layout anpassen
    plt.tight_layout()

    # Diagramm speichern
    output_path = os.path.join(os.path.dirname(__file__), "ja_nein_eval15.pdf")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")

    # Diagramm anzeigen
    plt.show()


def lokal_show_punkte():
    table = RI.get_table()
    table = RI.apply_instance(table)
    table = RI.apply_args(table)
    table = RI.get_mean(table)

    table["nein_instanze"] = table["file"].apply(
        lambda x: True if "change" in x.lower() or "move" in x.lower() else False
    )

    # Vorbereitung der Daten für das Punktdiagramm
    plot_data = []

    # Sammle alle Datenpunkte
    for index, row in table.iterrows():
        # Runtime extrahieren (in Sekunden)
        runtime = row.get("runtime", 0) + row.get("pre_time", 0)
        if runtime <= 0:
            continue  # Skip if runtime is not valid

        file = row["file"]
        numbers = re.findall(r"\d+", file)
        node_name = int(numbers[1]) if len(numbers) > 1 else 0

        # Bestimme ob es sich um eine Nein-Instanz handelt
        is_nein_instanze = row["nein_instanze"]
        group_label = "Nein-Instanzen" if is_nein_instanze else "Ja-Instanzen"

        plot_data.append(
            {
                "group": group_label,
                "runtime": runtime,
                "node_count": node_name,
                "is_nein": is_nein_instanze,
                "timeout": runtime >= TIMEOUT,
            }
        )

    if not plot_data:
        print("Keine gültigen Daten zum Plotten gefunden!")
        return

    # DataFrame für Plotting erstellen
    df_plot = pd.DataFrame(plot_data)

    # Seaborn Style setzen
    sns.set_style("whitegrid")
    plt.figure(figsize=(16, 10))

    # Punktdiagramm erstellen - getrennt nach Gruppen
    groups = df_plot["group"].unique()
    colors = ["green", "red"]  # Grün für Ja-Instanzen, Rot für Nein-Instanzen
    markers = ["o", "o"]  # Kreise für Ja-Instanzen, Quadrate für Nein-Instanzen

    for i, group in enumerate(groups):
        group_data = df_plot[df_plot["group"] == group]

        # Normale Punkte (nicht Timeout)
        normal_data = group_data[~group_data["timeout"]]
        if len(normal_data) > 0:
            plt.scatter(
                normal_data["runtime"],
                normal_data["node_count"],
                label=group,
                color=colors[i],
                marker=markers[i],
                s=80,
                alpha=0.7,
                edgecolors="black",
                linewidths=0.5,
            )

        # Timeout-Punkte (falls vorhanden)
        timeout_data = group_data[group_data["timeout"]]
        if len(timeout_data) > 0:
            plt.scatter(
                timeout_data["runtime"],
                timeout_data["node_count"],
                color=colors[i],
                marker="x",
                s=120,
                alpha=0.8,
                linewidths=2,
            )

    # Diagramm anpassen
    plt.xlabel("Laufzeit (Sekunden)", fontsize=LABEL_FONT_SIZE)
    plt.ylabel("Knotenzahl", fontsize=LABEL_FONT_SIZE)
    # plt.title("Punktdiagramm - Ja/Nein Instanzen", fontsize=TITEL_FONT_SIZE)

    # Timeout-Linie hinzufügen
    plt.axvline(x=TIMEOUT, color="red", linestyle="--", linewidth=2, alpha=0.7)

    # Timeout-Text hinzufügen
    plt.text(
        TIMEOUT + 80,
        plt.ylim()[1] * 0.9,
        f"Timeout ({TIMEOUT}s)",
        rotation=90,
        verticalalignment="center",
        horizontalalignment="right",
        fontsize=ACHSEN_FONT_SIZE,
        color="red",
        alpha=0.8,
    )

    # Legende anpassen
    plt.legend(
        title="Instanz-Typ",
        bbox_to_anchor=(1.05, 1),
        loc="upper left",
        fontsize=LEGENDE_FONT_SIZE,
        title_fontsize=LEGENDE_FONT_SIZE,
    )

    # Achsen-Tick-Größen anpassen
    plt.gca().tick_params(axis="both", which="major", labelsize=ACHSEN_FONT_SIZE)

    # Grid für bessere Lesbarkeit
    plt.grid(True, alpha=0.3)

    # Layout anpassen
    plt.tight_layout()

    # Diagramm speichern
    output_path = os.path.join(os.path.dirname(__file__), "punkte_eval15.pdf")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")

    # Diagramm anzeigen
    plt.show()


if __name__ == "__main__":
    if False:
        slurminade.update_default_configuration(
            # Your supervisor will tell you these details
            partition="alg",  # Which partition to use. Usually group name.
            constraint="alggen05",  # Which workstations within the partition to use
            exclusive=True,  # To use all cores on a node exclusively
            mail_type="FAIL",  # Send mail on failure
            mail_user="f.alich@tu-braunschweig.de",  # Mail to this address
        )
        run_list = RI.get_run_list()
        with slurminade.JobBundling(max_size=7):
            for key in run_list:
                run_solver_on_inst.distribute(key)

        slurminade.join()
        compress_results.distribute()
    else:
        # lokal_show_balken()
        lokal_show_kaktus()
        lokal_show_punkte()
        # lokal_show_ja_nein()

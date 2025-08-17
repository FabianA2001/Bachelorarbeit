import os
import re
from dataclasses import asdict

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from dc_triangulation import Cadical, Cadical_Parameter, Run_Algbench

# Font-Konstanten aus run_algbench
TITEL_FONT_SIZE = 20
LABEL_FONT_SIZE = 15
ACHSEN_FONT_SIZE = 12
LEGENDE_FONT_SIZE = 20

TIMEOUT = 300
path = os.path.join(os.path.dirname(__file__), "instances")
lokal_benchmark = os.path.join(os.path.dirname(__file__), "lokal_benchmark")
# This is the entry point for the evaluation script
# It will run the Run_Instance class from run_algbench module
outer_parameter = {
    Cadical: [
        {
            "timeout": TIMEOUT,
            "args": asdict(
                Cadical_Parameter(
                    degree=True,
                    intersection=True,
                    fix_hull=True,
                    # save_state=True,
                    optimize_propagation=True,
                    exclude_edges=True,
                )
            ),
        },
    ]
}

RI = Run_Algbench(
    inst_path=path,
    outer_parameter=outer_parameter,
    figure_path=os.path.dirname(__file__),
    path_benchmark=lokal_benchmark,
    host=["DESKTOP-L2QBIO4"],
)


def draw(table):
    # Vorbereitung der Daten für das Diagramm
    plot_data = []

    grouped = table.groupby("instance")
    for instance_name, instance_group in grouped:
        for index, row in instance_group.iterrows():
            counter = row["solution"]["counter"]
            file = row["file"]

            # Extrahiere die erste Zahl am Anfang des Dateinamens
            match_first = re.match(r"^(\d+)", file)
            first_number = int(match_first.group(1)) if match_first else 0

            # Extrahiere die zweite Zahl (Knotennummer) aus dem Dateinamen
            # Suche nach einer zweiten Zahl im Dateinamen
            numbers = re.findall(r"\d+", file)
            node_number = int(numbers[1]) if len(numbers) > 1 else 0

            # Bestimme ob "move" oder "change" im Dateinamen steht
            operation_type = ""
            if "move" in file.lower():
                operation_type = "_move"
            elif "change" in file.lower():
                operation_type = "_change"

            # Erstelle X-Achsen Label: "ErsteZahl_Knoten_Operation" (für Gruppierung)
            x_label = f"{first_number}_{node_number}{operation_type}"

            # Erstelle Display Label: "Knoten_Operation" (ohne erste Zahl, für Anzeige)
            display_label = f"{node_number}{operation_type}"

            plot_data.append(
                {
                    "instance": instance_name,
                    "file": file,
                    "first_number": first_number,
                    "node_number": node_number,
                    "operation_type": operation_type,
                    "x_label": x_label,
                    "display_label": display_label,
                    "counter": counter,
                }
            )

    # DataFrame für Plotting erstellen
    df_plot = pd.DataFrame(plot_data)

    # Seaborn Style setzen
    sns.set_style("whitegrid")
    plt.figure(figsize=(16, 8))

    # Line Plot mit verschiedenen Farben für verschiedene Instanzen
    # Verwende x_label für x-Achse

    # sns.scatterplot(
    #     data=df_plot, x="x_label", y="counter", hue="instance", s=100, alpha=0.7
    # )

    sns.lineplot(
        data=df_plot,
        x="x_label",
        y="counter",
        hue="instance",
        marker="o",
        markersize=8,
        linewidth=2,
    )

    # Diagramm anpassen
    # plt.title(
    #     "Counter vs. Node Number & Operation by Instance",
    #     fontsize=TITEL_FONT_SIZE,
    #     fontweight="bold",
    # )
    plt.xlabel("Knoten Anzahl", fontsize=LABEL_FONT_SIZE)
    plt.ylabel("Anzahl", fontsize=LABEL_FONT_SIZE)

    # Erstelle Custom X-Tick Labels ohne die erste Nummer
    unique_x_labels = sorted(df_plot["x_label"].unique())
    unique_display_labels = []
    for x_label in unique_x_labels:
        # Finde das entsprechende display_label für dieses x_label
        display_label = df_plot[df_plot["x_label"] == x_label]["display_label"].iloc[0]
        unique_display_labels.append(display_label)

    plt.xticks(
        range(len(unique_x_labels)), unique_display_labels, rotation=45, ha="right"
    )
    plt.legend(
        title="Instanz",
        bbox_to_anchor=(1.05, 1),
        loc="upper left",
        fontsize=LEGENDE_FONT_SIZE,
    )

    # Achsen-Tick-Größen anpassen
    plt.gca().tick_params(axis="both", which="major", labelsize=ACHSEN_FONT_SIZE)

    # Layout anpassen und speichern
    plt.tight_layout()

    # Diagramm speichern
    output_path = os.path.join(
        os.path.dirname(__file__), "counter_vs_first_node_operation_by_instance.pdf"
    )
    plt.savefig(output_path, dpi=300, bbox_inches="tight")

    # Diagramm anzeigen
    plt.show()


if __name__ == "__main__":
    table = RI.get_table()
    table = RI.apply_instance(table)
    table = RI.apply_args(table)
    draw(table)

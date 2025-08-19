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
path = os.path.join(os.path.dirname(__file__), "instances")
# This is the entry point for the evaluation script
# It will run the Run_Instance class from run_algbench module
outer_parameter = {
    Ortools: [
        {
            "timeout": TIMEOUT,
            "args": asdict(
                Ortools_Parameter(
                    intersection=True, degree=True, fix_hull=True, all_edges=True
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


def lokal_show():
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


if __name__ == "__main__":
    if False:
        slurminade.update_default_configuration(
            # Your supervisor will tell you these details
            partition="alg",  # Which partition to use. Usually group name.
            constraint="alggen04",  # Which workstations within the partition to use
            exclusive=True,  # To use all cores on a node exclusively
            mail_type="FAIL",  # Send mail on failure
            mail_user="f.alich@tu-braunschweig.de",  # Mail to this address
        )
        run_list = RI.get_run_list()
        with slurminade.JobBundling(max_size=10):
            for key in run_list:
                run_solver_on_inst.distribute(key)

        slurminade.join()
        compress_results.distribute()
    else:
        lokal_show()

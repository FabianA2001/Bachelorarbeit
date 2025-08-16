import logging
import os

import slurminade
from algbench import read_as_pandas
from dc_triangulation import Count, Graph_Wrapper, Run_Algbench, load_nodes_from_json

TIMEOUT = 4000

path = os.path.join(os.path.dirname(__file__), "instances")
lokal_benchmark_path = os.path.join(os.path.dirname(__file__), "lokal_benchmark")

outer_parameter = {
    Count: [
        {
            "timeout": TIMEOUT,
        },
    ]
}


RI = Run_Algbench(
    inst_path=path,
    outer_parameter=outer_parameter,
    figure_path=os.path.dirname(__file__),
    # host=["algry01", "algry02", "algry03", "algry04"],
    path_benchmark=lokal_benchmark_path,
)


from functools import reduce


def berechne_schnitt(*listen):
    """Gibt die gemeinsamen Elemente aller Listen zurück (als Set)."""
    return set.intersection(*(set(l) for l in listen))


def berechne_ausser_schnitt(*listen):
    """Gibt alle Elemente zurück, die nicht in allen Listen vorkommen (symmetrische Differenz)."""
    return reduce(lambda a, b: a ^ b, (set(l) for l in listen))


def show_lokal():
    table = read_as_pandas(
        RI.path_benchmark,
        lambda result: {
            "host": result["env"]["hostname"],
            "solver": result["parameters"]["args"]["solver_name"],
            "instance": result["parameters"]["args"]["instance_name"],
            "file": result["parameters"]["args"]["file_name"],
            "correct": result["result"]["correct"],
            "args": result["parameters"]["args"]["parameter"].get("args", {}),
            "evaluation": result["result"]["evaluation"],
            "timeout": result["parameters"]["args"]["parameter"]["timeout"],
            # "runtime": result["runtime"],
            "runtime": result["result"]["time_solver"],
            "pre_time": result["result"]["time_pre_solver"],
            "count": result["result"].get("solution", {}).get("count", -1),
            "seen_combinations": result["result"]
            .get("solution", {})
            .get("seen_combinations", {}),
        },
    )
    # # Filter nach Host, falls host angegeben ist
    # table = table[table["host"].isin(RI.host)]

    if RI.instances:
        table = table[table["instance"].isin(RI.instances)]

        all_instance = [
            key for inst in RI.instances for key in RI.instances[inst].keys()
        ]
        table = table[table["file"].isin(all_instance)]

    table["args_str"] = table["args"].apply(lambda x: str(x))
    # Gruppiere nach solver, instance, file, args und behalte nur die Zeile mit dem höchsten Timeout
    table = table.loc[
        table.groupby(["solver", "instance", "file", "args_str"])["timeout"].idxmax()
    ]
    solvers_name = [solver.NAME for solver in RI.solvers]
    table = table[table["solver"].isin(solvers_name)]

    # Kombiniere Instanz und Dateiname für die x-Achse
    table["instance_file"] = table["instance"] + "/" + table["file"]

    if table.empty:
        logging.warning("Keine Daten für die angegebene Konfiguration gefunden.")
        return

    table = table.sort_values(by=["instance_file"])

    # show werte von count für jede Zeile in instance_file
    info = ""
    info += f"Anzahl der Instanzen: {len(table['instance_file'].unique())}\n"
    for _, row in table.iterrows():
        str_row = f"{row['instance_file']}: count = "
        str_row = str_row.ljust(50)
        str_row += str(row["count"])
        info += str_row + "\n"
        if row["count"] > 1:
            vlaue = row["seen_combinations"][:-1]
            assert len(vlaue) <= 2, (
                f"Größer nicht implementiert, für größe {len(vlaue)}"
            )
            sets = [
                set((edge[0], edge[1]) for edge in vlaue[i]) for i in range(len(vlaue))
            ]
            schnitt = sets[0].intersection(sets[1])
            for i in range(2):
                nodes = load_nodes_from_json(
                    os.path.join(
                        os.path.dirname(__file__),
                        "instances",
                        row["instance"],
                        f"{row['file']}.json",
                    )
                )
                graph = Graph_Wrapper(nodes)
                # Kanten die in sets[i] sind aber nicht im anderen Set
                auuser_schnitt = sets[i] - sets[1 - i]
                for edge in auuser_schnitt:
                    graph.add_edge(edge[0], edge[1])
                for edge in schnitt:
                    graph.add_edge(edge[0], edge[1], False)
                    graph.edge_show_false(edge[0], edge[1])
                graph.name = str(f"{row['instance_file']}_{i}")
                graph.show_and_save(
                    show=False,
                    block=False,
                    save=os.path.join(
                        os.path.dirname(__file__),
                        "figures",
                    ),
                    show_set_false=True,
                    draw_name=False,
                    all_green=True,
                )
    logging.info(info)

    # Generiere LaTeX-Tabelle
    draw_table_as_latex(table)

    return table


def draw_table_as_latex(table):
    """
    Erstellt eine LaTeX-Tabelle aus der Pandas-Tabelle.
    Zeilen: Dateinamen (z.B. 30_1, 30_2, 40_1, etc.)
    Spalten: Instanzarten (d_flips, delaunay, greedy, iterative, random)
    """
    import re

    if table is None or table.empty:
        print("Keine Daten für LaTeX-Tabelle verfügbar.")
        return

    # Extrahiere Größe und Index aus den Dateinamen
    def extract_size_and_index(filename):
        # Beispiel: "000_d_flips_30" -> (30, 1), "001_d_flips_30" -> (30, 2)
        match = re.search(r"(\d+)_.*_(\d+)", filename)
        if match:
            file_index = int(match.group(1))
            size = int(match.group(2))
            # Konvertiere file_index zu 1-basiertem Index (000->1, 001->2, etc.)
            instance_index = (file_index % 2) + 1
            return f"{size}_{instance_index}"
        return filename

    # Erstelle eine neue Spalte für die Zeilen-Labels
    table_copy = table.copy()
    table_copy["row_label"] = table_copy["file"].apply(extract_size_and_index)

    # Erstelle Pivot-Tabelle: Zeilen=row_label, Spalten=instance, Werte=count
    pivot_table = table_copy.pivot_table(
        index="row_label",
        columns="instance",
        values="count",
        aggfunc="first",  # Falls mehrere Werte, nehme den ersten
    )

    # Sortiere die Zeilen nach Größe und Index
    def sort_key(row_label):
        if "_" in row_label:
            size, idx = row_label.split("_")
            return (int(size), int(idx))
        return (float("inf"), 0)

    pivot_table = pivot_table.reindex(sorted(pivot_table.index, key=sort_key))

    # Sortiere die Spalten in gewünschter Reihenfolge
    desired_columns = ["d_flips", "delaunay", "greedy", "iterative", "random"]
    available_columns = [col for col in desired_columns if col in pivot_table.columns]
    pivot_table = pivot_table[available_columns]

    # Ersetze NaN-Werte durch '-'
    pivot_table = pivot_table.fillna("-")

    # Generiere LaTeX-Code
    latex_code = "\\begin{table}[htbp]\n"
    latex_code += "\\centering\n"
    latex_code += "\\begin{tabular}{|l|" + "c|" * len(pivot_table.columns) + "}\n"
    latex_code += "\\hline\n"

    # Header
    header = "Knoten Anzahl & " + " & ".join(pivot_table.columns) + " \\\\\n"
    header = header.replace("_", " ")  # Escape underscores for LaTeX
    header = header.replace("d flips", "Delaunay Flips")  # Escape underscores for LaTeX
    header = header.replace("delaunay", "Delaunay")  # Escape underscores for LaTeX
    header = header.replace("greedy", "Greedy")  # Escape underscores for LaTeX
    header = header.replace("iterative", "Iterative")  # Escape underscores for LaTeX
    header = header.replace("random", "Random")  # Escape underscores for LaTeX
    latex_code += header
    latex_code += "\\hline\n"

    # Datenzeilen
    for row_label, row_data in pivot_table.iterrows():
        row_str = (
            str(row_label.replace("_", "\\_"))  # Ersetze '_' durch Leerzeichen
            + " & "
            + " & ".join(str(val) for val in row_data)
            + " \\\\\n"
        )
        latex_code += row_str

    latex_code += "\\hline\n"
    latex_code += "\\end{tabular}\n"
    latex_code += "\\caption{Ergebnisse der Triangulation nach Instanztyp und Größe}\n"
    latex_code += "\\label{tab:triangulation_results}\n"
    latex_code += "\\end{table}\n"

    # print("LaTeX-Tabelle:")
    # print(latex_code)

    # Speichere auch in Datei
    output_file = os.path.join(os.path.dirname(__file__), "latex_table.tex")
    with open(output_file, "w") as f:
        f.write(latex_code)

    print(f"\nLaTeX-Tabelle wurde auch gespeichert in: {output_file}")

    return latex_code


@slurminade.slurmify()
def run_solver_on_inst(key: str):
    RI.add_entrys(key, 1)


@slurminade.slurmify(mail_type="ALL")
def compress_results():
    # Compress the results to save significant disk space
    RI.compress()


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
        # with slurminade.JobBundling(max_size=10):
        for key in run_list:
            run_solver_on_inst.distribute(key)

        slurminade.join()
        compress_results.distribute()
    else:
        table = show_lokal()
        draw_table_as_latex(table)

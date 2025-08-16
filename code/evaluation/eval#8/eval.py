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
    # Filter nach Host, falls host angegeben ist
    table = table[table["host"].isin(RI.host)]

    if RI.instances:
        table = table[table["instance"].isin(RI.instances)]

        all_instance = [
            key for inst in RI.instances for key in RI.instances[inst].keys()
        ]
        table = table[table["file"].isin(all_instance)]

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
                )
    logging.info(info)


@slurminade.slurmify()
def run_solver_on_inst(key: str):
    RI.add_entrys(key, 1)


@slurminade.slurmify(mail_type="ALL")
def compress_results():
    # Compress the results to save significant disk space
    RI.compress()


if __name__ == "__main__":
    if True:
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
        show_lokal()

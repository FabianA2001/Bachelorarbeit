import logging
import os
from dataclasses import asdict

import slurminade
from algbench import read_as_pandas
from dc_triangulation import Count, Graph_Wrapper, Run_Algbench

asdict
TIMEOUT = 300
path = os.path.join(os.path.dirname(__file__), "instances")

# 1,2,3,6,7,8
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
    host=["algry01", "algry02", "algry03", "algry04"],
)


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
            "count": result["result"].get("solution", {}).get("count", {}),
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
    table = table.drop(columns=["file"])

    if table.empty:
        logging.warning("Keine Daten für die angegebene Konfiguration gefunden.")
        return

    table = table.sort_values(by=["instance_file"])

    # show werte von count für jede Zeile in instance_file
    print("Count values for each instance_file:")
    for _, row in table.iterrows():
        str_row = f"{row['instance_file']}: count = "
        str_row = str_row.ljust(50)
        str_row += str(row["count"])
        print(str_row)


@slurminade.slurmify()
def run_solver_on_inst(key: str):
    solver, nodes, possible, inst, file_name = RI.get_solver_inst_from_runlist[key]
    parameters = RI.outer_parameter[solver]
    for parameter in parameters:
        graph = Graph_Wrapper(nodes)
        RI.benchmark.add(
            RI.create_benchmark_entry,
            solver_name=solver.NAME,
            parameter=parameter,
            instance_name=inst,
            file_name=file_name,
            _possible=possible,
            _solver_type=solver,
            _graph=graph,
        )


@slurminade.slurmify(mail_type="ALL")
def compress_results():
    # Compress the results to save significant disk space
    RI.compress()


if __name__ == "__main__":
    if False:
        slurminade.update_default_configuration(
            # Your supervisor will tell you these details
            partition="alg",  # Which partition to use. Usually group name.
            constraint="alggen03",  # Which workstations within the partition to use
            exclusive=True,  # To use all cores on a node exclusively
            mail_type="FAIL",  # Send mail on failure
            mail_user="f.alich@tu-braunschweig.de",  # Mail to this address
        )
        run_list = RI.get_run_list()
        for key in run_list:
            run_solver_on_inst.distribute(key)

        slurminade.join()
        compress_results.distribute()
    else:
        show_lokal()

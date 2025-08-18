import logging
import os
import random

import pandas as pd
from algbench import read_as_pandas
from dc_triangulation import Count, Run_Algbench, load_nodes_from_json

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


def get_table():
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
            "run_seed": result["result"].get("run_seed", 0),
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
        return pd.DataFrame()

    table = table.sort_values(by=["instance_file"])
    return table


def generate_dict(table):
    instance_dict = {}

    for _, row in table.iterrows():
        key = row["instance_file"].replace("/", "_")
        data = row["seen_combinations"]
        data = list(data)
        data_length = len(data)
        nodes = load_nodes_from_json(
            os.path.join(
                os.path.dirname(__file__),
                "instances",
                row["instance"],
                f"{row['file']}.json",
            )
        )
        seed = row["run_seed"]
        assert seed != 0, "Seed should not be 0"
        random.seed(seed)
        random.shuffle(nodes)
        edges = []
        if data_length == 2:
            for edge in data[0]:
                edges.append((nodes[edge[0]].pos, nodes[edge[1]].pos))
        elif data_length == 3:
            for edge in data[0]:
                edges.append((nodes[edge[0]].pos, nodes[edge[1]].pos))
            for edge in data[1]:
                if edge not in data[0]:
                    edges.append((nodes[edge[0]].pos, nodes[edge[1]].pos))
        instance_dict[key] = edges
    return instance_dict


if __name__ == "__main__":
    import json

    table = get_table()
    instance_dict = generate_dict(table)

    # Speichere das Dictionary als JSON-Datei
    output_file = os.path.join(os.path.dirname(__file__), "calculated_data.json")
    with open(output_file, "w") as f:
        json.dump(dict(instance_dict), f, indent=2)

    print(f"Dictionary wurde gespeichert in: {output_file}")
    print(f"Anzahl der Instanzen: {len(instance_dict)}")

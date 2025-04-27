import os
from graph_utils import graph_const
from solver.solver import Solver
from graph_utils.graph_const import RESULTS_DIR
import json
from graph_utils.graph_wrapper import Graph_Wrapper
from graph_utils.node import load_nodes_from_json
import time
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd


def get_instances() -> dict[str, dict[str, str]]:
    """Lädt alle Ordner aus dem graph_const.INSTANCES_DIR Verzeichnis."""
    instances_dir = graph_const.PREFIX_INSTANCE
    instances = {}
    inst_names = [
        folder
        for folder in os.listdir(instances_dir)
        if os.path.isdir(os.path.join(instances_dir, folder))
    ]
    for inst_name in inst_names:
        inst_dir = os.path.join(instances_dir, inst_name)
        instances[inst_name] = {
            file.replace(".json", ""): os.path.join(inst_dir, file)
            for file in os.listdir(inst_dir)
            if file.endswith(".json")
        }
    return instances


def save_result(
    instance_name: str,
    algorithm_name: str,
    instance_file_name: str,
    time: float,
    success: bool = True,
):
    filename = f"{instance_name}.json"
    path = os.path.join(RESULTS_DIR, filename)

    # Laden oder leeres dict erstellen
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
    else:
        data = {}

    # Stelle sicher, dass der Algo existiert
    if algorithm_name not in data:
        data[algorithm_name] = {}

    new_entries = {instance_file_name: {"time": time, "success": success}}

    # Aktualisiere nur diesen Algo
    data[algorithm_name].update(new_entries)

    # Zurückschreiben in Datei
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def run_solver_on_instance(
    solver: Solver, instance_name: str, timeout: int = -1, algo_suffix_name: str = ""
):
    instance = get_instances()[instance_name]
    for file_name, file_path in instance.items():
        nodes = load_nodes_from_json(file_path)
        graph = Graph_Wrapper(nodes)
        solver.graph = graph
        starttime = time.time()
        success = solver.solve(timeout)
        duration = time.time() - starttime
        duration = round(duration, 2)
        solver_name = (
            f"{solver.name}_{algo_suffix_name}"
            if algo_suffix_name != ""
            else solver.name
        )
        save_result(instance_name, solver_name, file_name, duration, success)


def show_results(
    instance_name: str,
):
    with open(os.path.join(graph_const.RESULTS_DIR, instance_name), "r") as f:
        data = json.load(f)

    # In ein DataFrame umwandeln
    rows = []
    for algo_name, problems in data.items():
        for problem_name, info in problems.items():
            time = info["time"] if info["success"] else graph_const.FAIL_VALUE
            rows.append(
                {
                    "Algorithm": algo_name,
                    "Problem": problem_name,
                    "Time": time,
                }
            )

    df = pd.DataFrame(rows)

    # Seaborn Barplot
    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=df,
        x="Problem",
        y="Time",
        hue="Algorithm",  # Dadurch werden die Balken nebeneinander gruppiert
        palette="muted",
    )

    plt.title(
        f"Vergleich der Laufzeiten (Time) für {instance_name.replace(".json", "")} je Problem"
    )
    plt.xticks(rotation=45)
    plt.grid(True, axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.show()

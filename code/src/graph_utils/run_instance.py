import os
from graph_utils import graph_const
from solver.solver import Solver
from graph_utils.graph_const import RESULTS_DIR
import json
from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from graph_utils.node import load_nodes_from_json
import logging
from algbench import Benchmark, read_as_pandas


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
            file.replace(".json", ""): os.path.join(inst_name, file)
            for file in os.listdir(inst_dir)
            if file.endswith(".json")
        }
    return instances


def save_result(
    instance_name: str,
    algorithm_name: str,
    instance_file_name: str,
    time: float,
    correct: bool = True,
    triangulation: list[tuple[str, str]] = [],
    Percentage: float = 0.0,
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

    new_entries = {
        instance_file_name: {
            "time": time,
            "correct": correct,
            "percentage": Percentage,
            "triangulation": triangulation,
        }
    }

    # Aktualisiere nur diesen Algo
    data[algorithm_name].update(new_entries)

    # Zurückschreiben in Datei
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def create_benchmark_entry(
    solver_type: type[Solver],
    solver_name: str,
    solver_version: int,
    instance_name: str,
    file_name: str,
    possible: bool,
    timeout: int,
    _graph: Graph_Wrapper,
):
    solver = solver_type(_graph)
    success = solver.solve(timeout)
    is_triangulation = _graph.check_if_triangulation_with_degree_constraint()
    result = success and is_triangulation
    correct = possible == result
    if is_triangulation and not possible:
        logging.error(
            f"{instance_name} - {solver.name} - {file_name} should not be possible, but triangulation was found."
        )

    return {
        "correct": correct,
        "evaluation": _graph.evaluate_graph(),
        "triangulation": _graph.get_all_edges(True),
    }


def run_solver_on_instance(
    solver_type: type[Solver],
    instance_name: str,
    benchmark_path: str,
    timeout: int = -1,
):
    instance = get_instances()
    if instance_name not in instance.keys():
        raise ValueError(
            f"Instance {instance_name} not found in {graph_const.PREFIX_INSTANCE}"
        )
    benchmark = Benchmark(benchmark_path)
    benchmark.capture_logger("my_alg", logging.INFO)
    instance = instance[instance_name]
    for file_name, file_path in instance.items():
        nodes = load_nodes_from_json(file_path)
        with open(f"{graph_const.PREFIX_INSTANCE}{file_path}", "r") as f:
            possible = json.load(f)["possible"]
        graph = Graph_Wrapper(nodes)
        benchmark.add(
            create_benchmark_entry,
            solver_type=solver_type,
            solver_name=solver_type.NAME,
            solver_version=solver_type.VERSION,
            instance_name=instance_name,
            file_name=file_name,
            possible=possible,
            timeout=timeout,
            _graph=graph,
        )
    benchmark.compress()


def show_results(path: str):
    table = read_as_pandas(
        path,
        lambda result: {
            "solver": result["parameters"]["args"]["solver_name"],
            "instance": result["parameters"]["args"]["instance_name"],
            "file": result["parameters"]["args"]["file_name"],
            "correct": result["result"]["correct"],
            "evaluation": result["result"]["evaluation"],
            "runtime": result["runtime"],
        },
    )
    print(table)


# def show_results(instance_name: str, block: bool = False, ignore_correct: bool = False):
#     with open(f"{os.path.join(graph_const.RESULTS_DIR, instance_name)}.json", "r") as f:
#         data = json.load(f)

#     rows = []
#     for algo_name, problems in data.items():
#         # Sortiere die Probleme nach der führenden Nummer
#         for problem_name in sorted(problems.keys(), key=lambda x: int(x.split("_")[0])):
#             info = problems[problem_name]
#             if ignore_correct:
#                 time = info["time"]
#             else:
#                 time = info["time"] if info["correct"] else graph_const.FAIL_VALUE
#             rows.append(
#                 {
#                     "Algorithm": algo_name,
#                     "Problem": problem_name,
#                     "Time": time,
#                 }
#             )

#     df = pd.DataFrame(rows)

#     plt.figure(figsize=(12, 6))
#     sns.barplot(
#         data=df,
#         x="Problem",
#         y="Time",
#         hue="Algorithm",
#         palette="muted",
#     )

#     plt.title(f"Vergleich der Laufzeiten (Time) für {instance_name} je Problem")
#     plt.xticks(rotation=90)
#     plt.grid(True, axis="y", linestyle="--", alpha=0.7)
#     plt.tight_layout()
#     plt.show(block=block)


# def show_percentage_of_correct_nodes(instance_name: str, block: bool = False):
#     with open(f"{os.path.join(graph_const.RESULTS_DIR, instance_name)}.json", "r") as f:
#         data = json.load(f)

#     rows = []
#     for algo_name, problems in data.items():
#         # Sortiere die Probleme nach der führenden Nummer
#         for problem_name in sorted(problems.keys(), key=lambda x: int(x.split("_")[0])):
#             info = problems[problem_name]
#             percentage = info["percentage"]
#             rows.append(
#                 {
#                     "Algorithm": algo_name,
#                     "Problem": problem_name,
#                     "Percentage": percentage,
#                 }
#             )

#     df = pd.DataFrame(rows)

#     plt.figure(figsize=(12, 6))
#     sns.barplot(
#         data=df,
#         x="Problem",
#         y="Percentage",
#         hue="Algorithm",
#         palette="muted",
#     )

#     plt.title(f"Vergleich der Prozentsätze (Percentage) für {instance_name} je Problem")
#     plt.xticks(rotation=90)
#     plt.grid(True, axis="y", linestyle="--", alpha=0.7)
#     plt.tight_layout()
#     plt.show(block=block)
#     plt.pause(1)


# def show_triangulation_from_result(
#     instance_name: str,
#     algorithm_name: str,
#     instance_file_name: str,
#     result_file_name: str,
# ):
#     nodes = load_nodes_from_json(
#         f"{os.path.join(instance_name, instance_file_name)}.json"
#     )
#     with open(
#         os.path.join(graph_const.RESULTS_DIR, f"{result_file_name}.json"), "r"
#     ) as f:
#         data = json.load(f)
#     triangulation = data[algorithm_name][instance_file_name]["triangulation"]
#     graph = Graph_Wrapper(nodes)
#     for edge in triangulation:
#         graph.add_edge(edge[0], edge[1], active=True)
#     graph.show_and_save(show=True, save=True)

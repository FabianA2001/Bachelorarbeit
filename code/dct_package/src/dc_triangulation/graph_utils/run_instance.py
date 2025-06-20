import json
import logging
import os
import socket

import matplotlib.pyplot as plt
import pandas as pd
import questionary
import seaborn as sns
from algbench import Benchmark, read_as_pandas

from ..solver.solver import Solver
from ..utils import format_dictionary
from . import graph_const
from .graph_wrapper.graph_wrapper import Graph_Wrapper
from .node import load_nodes_from_json

# TODO in eigenes Projekt


class Run_Instance:
    DEFAULT_TIME = 30  # Default timeout for solvers in seconds

    def __init__(self, path_benchmark: str, solver: list) -> None:
        self.path_benchmark = path_benchmark
        self.benchmark = Benchmark(self.path_benchmark)
        self.benchmark.capture_logger("my_alg", logging.INFO)
        self.solvers_dict = {i.NAME: i for i in solver}
        pd.set_option("display.max_rows", None)
        pd.set_option("display.max_columns", None)
        pd.set_option("display.width", 200)

    @staticmethod
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

    @staticmethod
    def create_benchmark_entry(
        solver_type: type[Solver],
        solver_name: str,
        parameter: dict,
        instance_name: str,
        file_name: str,
        possible: bool,
        host: str,
        _graph: Graph_Wrapper,
    ):
        try:
            solver = solver_type(_graph)
            solution: dict = solver.solve(parameter)
        except Exception as e:
            logging.error(
                f"Error while solving {instance_name} - {solver_name} - {file_name} with {format_dictionary(parameter)}\n error:{e}"
            )
            return {
                "correct": False,
                "time_solver": -1,
                "time_pre_solver": -1,
                "evaluation": 0.0,
                "triangulation": [],
            }

        is_triangulation = _graph.check_if_triangulation_with_degree_constrained()
        result = solution["success"] and is_triangulation
        correct = possible == result
        if is_triangulation and not possible:
            logging.error(
                f"{instance_name} - {solver.name} - {file_name} should not be possible, but triangulation was found."
            )

        return {
            "correct": correct,
            "time_pre_solver": solver.pre_solve_time,
            "time_solver": solver.solve_time,
            "evaluation": _graph.evaluate_graph(),
            "triangulation": _graph.get_all_edges(True),
        }

    def save_default(self, data: dict):
        with open("./run_instance.json", "w") as f:
            json.dump(data, f, indent=4)

    def load_default(self) -> dict:
        """Lädt die Standardinstanzen und -solver aus der run_instance.json Datei."""
        with open("./run_instance.json", "r") as f:
            data = json.load(f)
        return data

    def run_solver_on_instance(
        self,
        solver_type: type[Solver],
        instance_name: str,
        parameter: dict,
    ):
        instance = self.get_instances()
        if instance_name not in instance.keys():
            raise ValueError(
                f"Instance {instance_name} not found in {graph_const.PREFIX_INSTANCE}"
            )
        instance = instance[instance_name]

        for file_name, file_path in instance.items():
            nodes = load_nodes_from_json(file_path)
            with open(f"{graph_const.PREFIX_INSTANCE}{file_path}", "r") as f:
                possible = json.load(f)["possible"]
            graph = Graph_Wrapper(nodes)
            self.benchmark.add(
                self.create_benchmark_entry,
                solver_type=solver_type,
                solver_name=solver_type.NAME,
                parameter=parameter,
                instance_name=instance_name,
                file_name=file_name,
                possible=possible,
                host=socket.gethostname(),
                _graph=graph,
            )
        self.benchmark.compress()

    def show_results(
        self,
        instances: list[str],
        solvers: list[type[Solver]],
        outer_parameter: dict,
        ignore_correct: bool = False,
        block: bool = False,
        host: str = socket.gethostname(),
    ):
        table = read_as_pandas(
            self.path_benchmark,
            lambda result: {
                "host": result["env"]["hostname"],
                "solver": result["parameters"]["args"]["solver_name"],
                "instance": result["parameters"]["args"]["instance_name"],
                "file": result["parameters"]["args"]["file_name"],
                "correct": result["result"]["correct"],
                "args": result["parameters"]["args"]["parameter"]["args"],
                "evaluation": result["result"]["evaluation"],
                "timeout": result["parameters"]["args"]["parameter"]["timeout"],
                # "runtime": result["runtime"],
                "runtime": result["result"]["time_solver"],
            },
        )
        # Filter nach Host, falls host angegeben ist
        if host:
            table = table[table["host"] == host]
            table = table.drop(columns=["host"])

        if not ignore_correct:
            # Setze runtime auf -1, wenn correct False ist
            table.loc[~table["correct"], "runtime"] = -1
            table = table.drop(columns=["correct"])

        if instances:
            table = table[table["instance"].isin(instances)]
        solvers_name = [solver.NAME for solver in solvers]
        if solvers:
            table = table[table["solver"].isin(solvers_name)]

        # Kombiniere Instanz und Dateiname für die x-Achse
        table["instance_file"] = table["instance"] + "/" + table["file"]
        table = table.drop(columns=["instance", "file"])

        all_args = []
        for arg_list in outer_parameter.values():
            for arg in arg_list:
                all_args.append(arg["args"])

        # Filter table to only include rows where args are in all_args
        table = table[table["args"].isin(all_args)]
        table["args_str"] = table["args"].apply(lambda x: str(x))

        # --- Timeout-Filter: Behalte nur Zeilen mit maximalem Timeout pro solver/instance_file ---
        # Sonderfall: -1 zählt als höchster Wert

        def timeout_rank(x):
            # -1 wird als sehr großer Wert behandelt
            return x.replace(-1, float("inf"))

        table["timeout_rank"] = timeout_rank(table["timeout"])
        idx = (
            table.groupby(["instance_file", "solver", "args_str"])[
                "timeout_rank"
            ].transform("max")
            == table["timeout_rank"]
        )
        table = table[idx]
        table = table.drop(columns=["timeout_rank"])

        # Create mapping from unique args to numbers, grouped by solver
        solver_args_mapping = {}
        solver_args_multiple = {}
        for solver in solvers_name:
            solver_table = table[table["solver"] == solver]
            unique_args = solver_table["args"].drop_duplicates().tolist()
            solver_args_mapping[solver] = {}
            solver_args_multiple[solver] = len(unique_args) > 1
            for i, args in enumerate(unique_args):
                timeout = solver_table[solver_table["args"] == args]["timeout"].iloc[0]
                solver_args_mapping[solver][str(args)] = (i + 1, args, timeout)

        def get_solver_args(row):
            solver = row["solver"]
            if solver_args_multiple[solver]:
                number = (solver_args_mapping[solver][str(row["args"])])[0]
                return f"{solver}-{number}"
            else:
                return solver

        table["solver_args"] = table.apply(get_solver_args, axis=1)
        table = table.drop(columns=["solver"])

        table = table.sort_values(by=["instance_file", "solver_args"])

        legend = ""
        legend += "\nArgs Legend Mapping (by Solver):"
        legend += "\n" + "=" * 50
        for solver, args_mapping in solver_args_mapping.items():
            legend += f"\n\n{solver}:"
            for args_dict_str, number_args in args_mapping.items():
                number = number_args[0]
                args_dict = number_args[1]
                # Find the original args dict from the string representation
                legend += f"\n|#{number} in {number_args[2]}s: {format_dictionary(args_dict, 2)}\n"
        legend = legend[:-1]
        legend += "\n" + "=" * 50
        logging.info(legend)

        self.create_plt(
            table=table,
            y="evaluation",
            block=False,
        )
        self.create_plt(
            table=table,
            y="runtime",
            block=block,
        )

    def create_plt(
        self,
        table,
        y: str,
        block: bool = False,
    ):
        plt.figure()
        sns.barplot(
            data=table,
            x="instance_file",
            y=y,
            hue="solver_args",
        )
        plt.title(f"{y.capitalize()} pro Instanz/File und Solver-Version")
        plt.xlabel("Instanz/Datei")
        plt.ylabel(y.capitalize())
        plt.xticks(rotation=90)
        plt.grid(True, axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.show(block=block)

    def run(
        self,
        insts: list[str],
        solvers: list[type[Solver]],
        outer_parameter: dict,
        ignore_correct: bool = False,
        host: str = socket.gethostname(),
        run: bool = True,
        show: bool = True,
    ):
        if run:
            for inst in insts:
                for solver in solvers:
                    if solver in outer_parameter:
                        list_parameter = outer_parameter[solver]
                    else:
                        logging.warning("No parameter found for solver, using default.")
                        list_parameter = [{"timeout": self.DEFAULT_TIME, "args": None}]
                    for parameter in list_parameter:
                        self.run_solver_on_instance(
                            solver_type=solver,
                            instance_name=inst,
                            parameter=parameter,
                        )
        # from algbench import describe
        # describe(self.path_benchmark)
        if show:
            self.show_results(
                insts, solvers, outer_parameter, ignore_correct, host=host
            )

    @staticmethod
    def get_selection(lit: list):
        selected_inst = []
        while True:
            selected_inst = questionary.checkbox(
                "Wähle eine oder mehrere Optionen:", choices=lit
            ).ask()
            if selected_inst:
                break
            print("Bitte wähle mindestens einen Wert aus.")
        return [str(i) for i in selected_inst]

    def select(
        self,
        outer_parameter: dict,
        host=socket.gethostname(),
        run: bool = True,
        show: bool = True,
    ):
        # Fragen nach Instanzen
        instances = self.get_instances()
        instances_names = sorted(list(instances.keys()))
        insts = self.get_selection(instances_names)

        # Frage nach Solver
        solvers = self.get_selection(list(self.solvers_dict.keys()))
        solvers = [self.solvers_dict[i] for i in solvers]

        ignore_correct = not questionary.confirm(
            "Ergebnisse mit falschen Triangulationen als -1 Darstellen?", default=True
        ).ask()

        # Frage, ob speichern, Standard ist Nein
        save = questionary.confirm(
            "Auswahl als Standard speichern?", default=True
        ).ask()
        if save:
            self.save_default(
                {
                    "instances": insts,
                    "solvers": [solver.NAME for solver in solvers],
                    "ignore_correct": ignore_correct,
                }
            )

        self.run(
            insts,
            solvers,
            outer_parameter,
            ignore_correct,
            host=host,
            run=run,
            show=show,
        )

    def run_default(
        self,
        outer_parameter: dict,
        host=socket.gethostname(),
        run: bool = True,
        show: bool = True,
    ):
        data = self.load_default()
        self.run(
            data.get("instances", []),
            [self.solvers_dict[i] for i in data.get("solvers", [])],
            outer_parameter=outer_parameter,
            ignore_correct=data.get("ignore_correct", True),
            host=host,
            run=run,
            show=show,
        )

    def show_triangulation_from_instance(
        self,
        instance_name: str,
        algorithm_name: str,
        instance_file_name: str,
        host=socket.gethostname(),
    ):
        table = read_as_pandas(
            self.path_benchmark,
            lambda result: {
                "host": result["env"]["hostname"],
                "solver": result["parameters"]["args"]["solver_name"],
                "instance": result["parameters"]["args"]["instance_name"],
                "file": result["parameters"]["args"]["file_name"],
                "tri": result["result"]["triangulation"],
            },
        )

        table = table[
            (table["instance"] == instance_name)
            & (table["solver"] == algorithm_name)
            & (table["file"] == instance_file_name)
            & (table["host"] == host)
        ]

        print(table)  # oder weitere Verarbeitung
        nodes = load_nodes_from_json(f"{instance_name}/{instance_file_name}.json")
        graph = Graph_Wrapper(nodes)
        if table.empty:
            logging.error(
                f"No results found for {instance_name} - {algorithm_name} - {instance_file_name} on host {host}"
            )
            return
        triangulation = table.iloc[0]["tri"]
        if triangulation is None:
            logging.error(
                f"No triangulation found for {instance_name} - {algorithm_name} - {instance_file_name} on host {host}"
            )
            return
        for edge in triangulation:
            graph.add_edge(edge[0], edge[1], active=True)
        graph.show_and_save()

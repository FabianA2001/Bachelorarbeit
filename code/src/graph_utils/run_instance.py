import os
from graph_utils import graph_const
from solver.solver import Solver
import json
from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from graph_utils.node import load_nodes_from_json
import logging
from algbench import Benchmark, read_as_pandas
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import socket
import questionary


class Run_Instance:
    DEFAULT_TIME = 30  # Default timeout for solvers in seconds

    def __init__(self, path_benchmark: str, solver: list) -> None:
        self.path_benchmark = path_benchmark
        self.benchmark = Benchmark(self.path_benchmark)
        self.benchmark.capture_logger("my_alg", logging.INFO)
        self.solvers_dict = {i.NAME: i for i in solver}
        pd.set_option("display.max_rows", None)

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
        solver = solver_type(_graph)
        solution: dict = solver.solve(parameter)
        is_triangulation = _graph.check_if_triangulation_with_degree_constraint()
        result = solution["success"] and is_triangulation
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
        instances: list[str] = [],
        solvers: list[type[Solver]] = [],
        only_newest: bool = True,
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
                "version": result["parameters"]["args"]["parameter"]["version"],
                "correct": result["result"]["correct"],
                "evaluation": result["result"]["evaluation"],
                "runtime": result["runtime"],
            },
        )
        # filter nach Host
        # table = table.sort_values(by=["solver", "instance", "file"])
        # Filter nach Host, falls host angegeben ist
        if host:
            table = table[table["host"] == host]
            table = table.drop(columns=["host"])

        if not ignore_correct:
            # Setze runtime auf -1, wenn correct False ist
            table.loc[~table["correct"], "runtime"] = -1
            table = table.drop(columns=["correct"])

        # self.create_plt(
        #     table=table,
        #     y="evaluation",
        #     block=False,
        #     instances=instances,
        #     solvers=[solver.NAME for solver in solvers],
        #     only_newest=only_newest,
        # )
        self.create_plt(
            table=table,
            y="runtime",
            block=block,
            instances=instances,
            solvers=[solver.NAME for solver in solvers],
            only_newest=only_newest,
        )

    def create_plt(
        self,
        table,
        y: str,
        block: bool = False,
        instances: list[str] = [],
        solvers: list[str] = [],
        only_newest: bool = True,
    ):
        if instances:
            table = table[table["instance"].isin(instances)]
        if solvers:
            table = table[table["solver"].isin(solvers)]

        # Kombiniere Instanz und Dateiname für die x-Achse

        table["instance_file"] = table["instance"] + "/" + table["file"]
        if only_newest:
            table["version_num"] = table["version"].astype(float)
            idx = (
                table.groupby(["solver", "instance_file"])["version_num"].transform(
                    "max"
                )
                == table["version_num"]
            )
            table = table[idx]
            table = table.drop(columns=["version_num"])

        table["solver_version"] = table["solver"] + " v" + table["version"].astype(str)
        table = table.sort_values(by=["solver_version", "instance_file"])
        plt.figure()
        sns.barplot(
            data=table,
            x="instance_file",
            y=y,
            hue="solver_version",
        )
        plt.title(
            f"{y.capitalize()} pro Instanz/File und Solver-Version"
            + (" (nur neueste Version)" if only_newest else "")
        )
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
        parameter: dict,
        only_newest: bool = True,
        ignore_correct: bool = False,
    ):
        for inst in insts:
            for solver in solvers:
                self.run_solver_on_instance(
                    solver_type=solver,
                    instance_name=inst,
                    parameter=parameter,
                )
        # from algbench import describe
        # describe(self.path_benchmark)
        self.show_results(insts, solvers, only_newest, ignore_correct)

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

    def select(self):
        # Fragen nach Instanzen
        instances = self.get_instances()
        instances_names = sorted(list(instances.keys()))
        insts = self.get_selection(instances_names)

        # Frage nach Solver
        solvers = self.get_selection(list(self.solvers_dict.keys()))
        solvers = [self.solvers_dict[i] for i in solvers]

        # Frage nach Timeout, Standard ist -1 Sekunden
        while True:
            timeout = questionary.text(
                "Timeout in Sekunden angeben (-1 = kein Timeout):", default="-1"
            ).ask()
            try:
                timeout = int(timeout)
            except ValueError:
                print("Bitte eine gültige Zahl eingeben.")
                continue
            if timeout < -1:
                print("Timeout muss größer oder gleich -1 sein.")
                continue
            elif timeout == 0:
                print("Timeout kann nicht 0 sein, bitte -1 für kein Timeout verwenden.")
                continue
            break

        while True:
            version = questionary.text(
                "Version der Parameter (z.B. 0.1, 0.2, ...):", default="0.1"
            ).ask()
            try:
                version = float(version)
            except ValueError:
                print("Bitte eine gültige Zahl eingeben.")
                continue
            if version < 0:
                print("Version muss größer oder gleich 0 sein.")
                continue
            break

        only_new = questionary.confirm(
            "Nur die neuste Version anzeigen?", default=True
        ).ask()

        ignore_correct = not questionary.confirm(
            "Ergebnisse mit falschen Triangulationen als -1 Darstellen?", default=True
        ).ask()

        # Frage, ob speichern, Standard ist Nein
        save = questionary.confirm(
            "Auswahl als Standard speichern?", default=False
        ).ask()
        if save:
            self.save_default(
                {
                    "instances": insts,
                    "solvers": [solver.NAME for solver in solvers],
                    "timeout": timeout,
                    "version": version,
                    "only_new": only_new,
                    "ignore_correct": ignore_correct,
                }
            )

        parameter = {"timeout": timeout, "version": version}

        self.run(insts, solvers, parameter, only_new, ignore_correct)

    def run_default(self):
        data = self.load_default()
        parameter = {
            "timeout": data.get("timeout", self.DEFAULT_TIME),
            "version": data.get("version", 0.1),
        }
        self.run(
            data.get("instances", []),
            [self.solvers_dict[i] for i in data.get("solvers", [])],
            parameter,
            only_newest=data.get("only_new", True),
            ignore_correct=data.get("ignore_correct", True),
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

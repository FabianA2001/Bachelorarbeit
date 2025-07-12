import json
import logging
import os
import socket

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from algbench import Benchmark, read_as_pandas

from .graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from .graph_utils.node import Node, load_nodes_from_json
from .solver.solver import Solver
from .utils import format_dictionary

"""
        insts: list[str],
        solvers: list[type[Solver]],
        outer_parameter: dict,
        ignore_correct: bool = False,
        host: str = socket.gethostname(),
        run: bool = True,
        show: bool = True,

"""


# TODO sollte aus dem Packet ausgelagert werden, verschieben bis es stört
class Run_Algbench:
    DEFAULT_TIME = 30  # Default timeout for solvers in seconds
    DEFAULT_BENCHMARK_PATH = "./benchmark"

    def __init__(
        self,
        inst_path: str,
        outer_parameter: dict,
        ignore_correct: bool = False,
        host: str = socket.gethostname(),
        path_benchmark: str = "",
        figure_path: str = "",
    ) -> None:
        self.inst_path = inst_path
        self.instances = self.get_instances(self.inst_path)
        self.outer_parameter = outer_parameter
        self.solvers = [solver for solver in self.outer_parameter.keys()]
        self.ignore_correct = ignore_correct
        self.host = host
        if path_benchmark == "":
            self.path_benchmark = self.DEFAULT_BENCHMARK_PATH
        else:
            self.path_benchmark = path_benchmark
        self.figure_path = figure_path
        self.get_solver_inst_from_runlist: dict[
            str, tuple[type[Solver], list[Node], bool, str, str]
        ] = {}
        self.setup_keys()

        self.benchmark = Benchmark(self.path_benchmark)
        self.benchmark.capture_logger(Solver.LOGGER_NAME)
        pd.set_option("display.max_rows", None)
        pd.set_option("display.max_columns", None)
        pd.set_option("display.width", 200)

    def delete_runlist(self):
        delete_list = []
        for (
            solver,
            nodes,
            possible,
            inst,
            file_name,
        ) in self.get_solver_inst_from_runlist.values():
            parameters = self.outer_parameter[solver]
            for para in parameters:
                delete_list.append(
                    (
                        solver.NAME,
                        inst,
                        file_name,
                        para["args"],
                    )
                )

        def func(dictionary: dict) -> bool:
            if (
                dictionary["parameters"]["args"]["solver_name"],
                dictionary["parameters"]["args"]["instance_name"],
                dictionary["parameters"]["args"]["file_name"],
                dictionary["parameters"]["args"]["parameter"]["args"],
            ) in delete_list and dictionary["env"]["hostname"] == self.host:
                return True
            return False

        self.benchmark.delete_if(func)

    def show_key_from_runlist(self, key: str):
        solver, nodes, possible, inst, file_name = self.get_solver_inst_from_runlist[
            key
        ]
        parameters = [para["args"] for para in self.outer_parameter[solver]]
        for entry in self.benchmark:
            if (
                entry["parameters"]["args"]["solver_name"] == solver.NAME
                and entry["parameters"]["args"]["instance_name"] == inst
                and entry["parameters"]["args"]["file_name"] == file_name
                and entry["env"]["hostname"] == self.host
                and entry["parameters"]["args"]["parameter"]["args"] in parameters
            ):
                logger = entry.get("logging", None)
                entry["logging"] = ""
                print(format_dictionary(entry))
                print("Logging:")
                if logger:
                    for dict in logger:
                        print(f"{dict['name']} : {dict['msg']}")

    def setup_keys(self):
        for inst in self.instances.keys():
            for solver in self.solvers:
                instance = self.instances[inst]

                for file_name in sorted(instance):
                    file_path = instance[file_name]
                    nodes = load_nodes_from_json(file_path)
                    with open(file_path, "r") as f:
                        possible = json.load(f)["possible"]
                    self.get_solver_inst_from_runlist[
                        f"{solver.NAME}_{inst}_{file_name}"
                    ] = (solver, nodes, possible, inst, file_name)

    @staticmethod
    def get_instances(path) -> dict[str, dict[str, str]]:
        """Lädt alle Ordner aus dem graph_const.INSTANCES_DIR Verzeichnis."""
        instances_dir = path
        instances = {}
        inst_names = [
            folder
            for folder in os.listdir(instances_dir)
            if os.path.isdir(os.path.join(instances_dir, folder))
        ]
        for inst_name in inst_names:
            inst_dir = os.path.join(instances_dir, inst_name)
            instances[inst_name] = {
                file.replace(".json", ""): os.path.join(path, inst_name, file)
                for file in os.listdir(inst_dir)
                if file.endswith(".json")
            }
        return instances

    @staticmethod
    def create_benchmark_entry(
        solver_name: str,
        parameter: dict,
        instance_name: str,
        file_name: str,
        _possible: bool,
        _solver_type: type[Solver],
        _graph: Graph_Wrapper,
    ):
        info = ""
        try:
            solver = _solver_type(_graph)
            solution: dict = solver.solve(parameter)
        except Exception as e:
            info += f"Error while solving: {e}\n"
            return {
                "correct": False,
                "time_solver": -1,
                "time_pre_solver": -1,
                "evaluation": 0.0,
                "triangulation": [],
                "info": info,
            }

        is_triangulation = _graph.check_if_triangulation_with_degree_constrained()
        result = solution["success"] and is_triangulation
        correct = _possible == result
        if is_triangulation and not _possible:
            info += f"{solver.name} on {instance_name}_{file_name} should not be possible, but triangulation was found.\n"

        return {
            "correct": correct,
            "time_pre_solver": solver.pre_solve_time,
            "time_solver": solver.solve_time,
            "timing": solver.timing,
            "evaluation": _graph.evaluate_graph(),
            "triangulation": _graph.get_all_edges(True),
            "info": info,
        }

        # @staticmethod
        # def run_solver_on_instance():

        # for file_name in sorted(instance):
        #     file_path = instance[file_name]
        #     nodes = load_nodes_from_json(file_path)
        #     with open(file_path, "r") as f:
        #         possible = json.load(f)["possible"]
        #     graph = Graph_Wrapper(nodes)
        #     timeout = [False]
        #     ####################################################
        #     # hack für eval 6
        #     if parameter.get("hack_eval_6", False):
        #         try:
        #             if "hack_eval_6_data" not in parameter:
        #                 raise ValueError(
        #                     "hack_eval_6_data must be provided in the parameter."
        #                 )
        #             if "hack_eval_6_PERCENT" not in parameter:
        #                 raise ValueError(
        #                     "hack_eval_6_PERCENT must be provided in the parameter."
        #                 )
        #             data = parameter["hack_eval_6_data"]
        #             percent = parameter["hack_eval_6_PERCENT"]
        #             key = f"{instance_name}_{file_name}.json"
        #             logging.info("-------------------------------------------->")
        #             logging.info(key)
        #             if key not in data:
        #                 raise ValueError(f"No data found for instance {key}.")
        #             if percent not in data[key]:
        #                 raise ValueError(
        #                     f"No data found for instance {key} with percent {percent}."
        #                 )
        #             parameter["debug_exclude_edges"] = data[key][percent]
        #         except ValueError as e:
        #             logging.error(f"Error in hack_eval_6: {e}")
        #             continue
        #     ############################################

        #     logging.info(f"starte instance: {instance_name}/{file_name}")
        #     self.benchmark.add(
        #         self.create_benchmark_entry,
        #         solver_type=solver_type,
        #         solver_name=solver_type.NAME,
        #         parameter=parameter,
        #         instance_name=instance_name,
        #         file_name=file_name,
        #         possible=possible,
        #         host=socket.gethostname(),
        #         _graph=graph,
        #         _timeout=timeout,
        #     )
        #     if timeout[0]:
        #         logging.warning(
        #             f"Timeout while solving {instance_name} - {solver_type.NAME} - {file_name} with {format_dictionary(parameter)}"
        #         )
        #         break

    def show(
        self,
        old: bool = False,
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
                "pre_time": result["result"]["time_pre_solver"],
            },
        )
        # Filter nach Host, falls host angegeben ist
        table = table[table["host"] == self.host]
        table = table.drop(columns=["host"])

        if not self.ignore_correct:
            # lösche zeilen wenn nicht correct
            table = table[table["correct"]]
            table = table.drop(columns=["correct"])

        if self.instances:
            table = table[table["instance"].isin(self.instances)]

            all_instance = [
                key for inst in self.instances for key in self.instances[inst].keys()
            ]
            table = table[table["file"].isin(all_instance)]

        solvers_name = [solver.NAME for solver in self.solvers]
        table = table[table["solver"].isin(solvers_name)]

        # Kombiniere Instanz und Dateiname für die x-Achse
        table["instance_file"] = table["instance"] + "/" + table["file"]
        table = table.drop(columns=["instance", "file"])

        all_args = []
        for arg_list in self.outer_parameter.values():
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

        if table.empty:
            logging.warning("Keine Daten für die angegebene Konfiguration gefunden.")
            return

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

        if table.empty:
            logging.warning("Keine Daten für die angegebene Konfiguration gefunden.")
            return

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

        # als Balkendiagramm darstellen
        if old:
            self.create_plt(
                table=table,
                y="pre_time",
                block=False,
            )
            self.create_plt(
                table=table,
                y="runtime",
                block=True,
            )
            return

        # Erstelle Cactus Plot
        self.create_cactus(
            table=table,
            y="pre_time",
            block=False,
        )
        self.create_cactus(
            table=table,
            y="runtime",
            block=True,
        )

    def create_cactus(
        self,
        table,
        y: str,
        block: bool = False,
    ):
        """
        Erstellt einen Cactus Plot für die Benchmark-Daten.
        In einem Cactus Plot wird die Zeit (y-Achse) gegen die Anzahl der gelösten
        Instanzen (x-Achse) dargestellt, sortiert nach Laufzeit.
        """

        # Seaborn Style setzen
        sns.set_style("whitegrid")

        # Debug: Zeige alle verfügbaren Solver
        all_solvers = table["solver_args"].unique()

        # Debug: Zeige Datenverteilung vor Filterung
        for solver in all_solvers:
            solver_count = len(table[table["solver_args"] == solver])
            positive_count = len(
                table[(table["solver_args"] == solver) & (table[y] >= 0)]
            )

        # Filter gültige Werte (entferne negative Werte wie -1 für Timeouts)
        valid_data = table[table[y] >= 0].copy()

        if len(valid_data) == 0:
            logging.warning(f"Keine gültigen Daten für {y} Cactus Plot gefunden")
            return

        # Eindeutige Solver ermitteln
        unique_solvers = valid_data["solver_args"].unique()

        # Seaborn Farbpalette
        colors = sns.color_palette("husl", len(unique_solvers))

        plt.figure(figsize=(12, 8))

        # Für jeden Solver die Daten sortieren und plotten
        for i, solver in enumerate(unique_solvers):
            solver_data = valid_data[valid_data["solver_args"] == solver][y].values

            if len(solver_data) == 0:
                logging.warning(f"Keine Daten für Solver '{solver}' nach Filterung")
                continue

            # Sortieren für Cactus Plot (wichtig!)
            times_sorted = np.sort(solver_data)
            y_values = np.arange(1, len(times_sorted) + 1)

            plt.plot(
                times_sorted,
                y_values,
                "o-",
                color=colors[i],
                label=solver,
                linewidth=2,
                markersize=3,
                alpha=0.8,
                drawstyle="steps-post",
            )

        # Styling (x und y Achsen getauscht)
        plt.xlabel(
            f"{y.replace('_', ' ').title()} (Sekunden)", fontsize=12, fontweight="bold"
        )
        plt.ylabel("Anzahl gelöste Instanzen", fontsize=12, fontweight="bold")
        plt.title(
            f"Cactus Plot - {y.replace('_', ' ').title()} Performance Vergleich",
            fontsize=14,
            fontweight="bold",
            pad=20,
        )

        # Legende styling
        legend = plt.legend(
            loc="upper left", fontsize=11, frameon=True, fancybox=True, shadow=True
        )
        legend.get_frame().set_facecolor("white")
        legend.get_frame().set_alpha(0.9)

        # Grid
        plt.grid(True, alpha=0.3, linestyle="-", linewidth=0.5)

        # X-Achse logarithmisch skalieren (oft nützlich bei Performance-Daten)
        if valid_data[y].max() / valid_data[y].min() > 10:  # Nur wenn große Spanne
            plt.xscale("log")

        # Seaborn despine für cleaner look
        sns.despine()

        # Layout optimieren
        plt.tight_layout()

        # Speichern falls Pfad angegeben
        if self.figure_path:
            plt.savefig(
                os.path.join(self.figure_path, f"cactus_{y}.pdf"),
                dpi=300,
                bbox_inches="tight",
            )

        plt.show(block=block)

    def create_plt(
        self,
        table,
        y: str,
        block: bool = False,
    ):
        # Bestimme ob eine gebrochene Y-Achse nötig ist
        y_values = table[y].dropna()
        y_values = y_values[
            y_values >= 0
        ]  # Entferne negative Werte (z.B. -1 für Timeouts)

        if len(y_values) == 0:
            # Fallback für den Fall, dass keine gültigen Werte vorhanden sind
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
            if self.figure_path:
                plt.savefig(os.path.join(self.figure_path, y + ".pdf"))
            return

        y_min, y_max = y_values.min(), y_values.max()
        y_range = y_max - y_min

        # Prüfe ob gebrochene Achse sinnvoll ist (große Spanne mit vielen kleinen Werten)
        if y_range > 0 and y_max > 10 * y_min and y_min > 0:
            # Erstelle gebrochene Y-Achse
            fig, (ax2, ax1) = plt.subplots(2, 1, sharex=True, figsize=(12, 8))
            fig.subplots_adjust(hspace=0.05)

            # Bestimme Break-Points
            break_point = y_min + y_range * 0.1  # Unten 10% der Spanne

            # Oberer Plot (hohe Werte) - ax2 ist jetzt oben
            sns.barplot(data=table, x="instance_file", y=y, hue="solver_args", ax=ax2)
            ax2.set_ylim(break_point, y_max * 1.1)
            ax2.set_ylabel(f"{y.capitalize()} (hohe Werte)")
            ax2.tick_params(axis="x", labelbottom=False)
            ax2.grid(True, axis="y", linestyle="--", alpha=0.7)

            # Unterer Plot (niedrige Werte) - ax1 ist jetzt unten
            sns.barplot(data=table, x="instance_file", y=y, hue="solver_args", ax=ax1)
            ax1.set_ylim(0, break_point)
            ax1.set_xlabel("Instanz/Datei")
            ax1.set_ylabel(f"{y.capitalize()} (niedrige Werte)")
            ax1.tick_params(axis="x", rotation=90)
            ax1.grid(True, axis="y", linestyle="--", alpha=0.7)

            # Entferne Legende vom unteren Plot
            ax1.legend().remove()

            # Break-Markierungen hinzufügen
            d = 0.015
            kwargs = dict(transform=ax1.transAxes, color="k", clip_on=False)
            ax1.plot((-d, +d), (1 - d, 1 + d), **kwargs)
            ax1.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)

            kwargs.update(transform=ax2.transAxes)
            ax2.plot((-d, +d), (-d, +d), **kwargs)
            ax2.plot((1 - d, 1 + d), (-d, +d), **kwargs)

            plt.suptitle(f"{y.capitalize()} pro Instanz/File und Solver-Version")

        else:
            # Normale Darstellung
            plt.figure(figsize=(12, 6))
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
        if self.figure_path:
            plt.savefig(os.path.join(self.figure_path, y + ".pdf"))

    def get_run_list(
        self,
    ) -> list[str]:
        return list(self.get_solver_inst_from_runlist.keys())

    def compress(self):
        self.benchmark.compress()

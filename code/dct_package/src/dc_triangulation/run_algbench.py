import json
import logging
import os
import random
import socket
import uuid

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from algbench import Benchmark, read_as_pandas

from .graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from .graph_utils.node import Node, load_nodes_from_json
from .solver.solver import Solver
from .utils import format_dictionary

NUMBER_RUNS_FOR_AVG = (
    5  # Anzahl der Durchläufe der gleichen Instanze für den Durchschnitt
)


# TODO sollte aus dem Packet ausgelagert werden, verschieben bis es stört
class Run_Algbench:
    DEFAULT_TIME = 30  # Default timeout for solvers in seconds
    DEFAULT_BENCHMARK_PATH = "./benchmark"

    def __init__(
        self,
        inst_path: str,
        outer_parameter: dict,
        ignore_correct: bool = False,
        host: list[str] = [socket.gethostname()],
        path_benchmark: str = "",
        figure_path: str = "",
        name: str = "",
    ) -> None:
        self.inst_path = inst_path
        self.instances = self.get_instances(self.inst_path)
        self.outer_parameter = outer_parameter
        self.solvers = [solver for solver in self.outer_parameter.keys()]

        self.solvers_name = [solver.NAME for solver in self.solvers]
        self.ignore_correct = ignore_correct
        self.host = host
        if path_benchmark == "":
            self.path_benchmark = self.DEFAULT_BENCHMARK_PATH
        else:
            self.path_benchmark = path_benchmark
        self.figure_path = figure_path
        self.name = name

        self.get_solver_inst_from_runlist: dict[
            str, tuple[type[Solver], list[Node], bool, str, str]
        ] = {}
        self.setup_keys()

        self.benchmark = Benchmark(self.path_benchmark)
        self.benchmark.capture_logger(Solver.LOGGER_NAME)
        self.number_benchmark_rows = len(self.benchmark)
        pd.set_option("display.max_rows", None)
        pd.set_option("display.max_columns", None)
        pd.set_option("display.width", 200)

    def get_run_number(self) -> int:
        self.number_benchmark_rows += 1
        return self.number_benchmark_rows

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
                        para.get("args", {}),
                    )
                )

        def func(dictionary: dict) -> bool:
            if (
                dictionary["parameters"]["args"]["solver_name"],
                dictionary["parameters"]["args"]["instance_name"],
                dictionary["parameters"]["args"]["file_name"],
                dictionary["parameters"]["args"]["parameter"].get("args", {}),
            ) in delete_list and dictionary["env"]["hostname"] in self.host:
                return True
            return False

        bevor_delete = len(self.benchmark)
        self.benchmark.delete_if(func)
        logging.info(
            f"Anzahl der Einträge von {bevor_delete} zu {len(self.benchmark)} reduziert."
        )

    def show_key_from_runlist(self, key: str, check_correct: bool = False):
        solver, nodes, possible, inst, file_name = self.get_solver_inst_from_runlist[
            key
        ]
        parameters = [para["args"] for para in self.outer_parameter[solver]]
        for entry in self.benchmark:
            if not check_correct:
                if entry["result"]["correct"]:
                    continue
            if (
                entry["parameters"]["args"]["solver_name"] == solver.NAME
                and entry["parameters"]["args"]["instance_name"] == inst
                and entry["parameters"]["args"]["file_name"] == file_name
                and entry["env"]["hostname"] in self.host
                and entry["parameters"]["args"]["parameter"]["args"] in parameters
            ):
                logger = entry.get("logging", None)
                entry["logging"] = ""
                print(format_dictionary(entry))
                print("Logging:")
                if logger:
                    for dict in logger:
                        print(f"{dict['name']} : {dict['msg']}")
        print(
            "-----------------------------------------------------------------------------------"
        )
        print(
            "-----------------------------------------------------------------------------------"
        )

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

    def get_table(self) -> pd.DataFrame:
        pass

        table = read_as_pandas(
            self.path_benchmark,
            lambda result: {
                "host": result["env"]["hostname"],
                "solver": result["parameters"]["args"]["solver_name"],
                "instance": result["parameters"]["args"]["instance_name"],
                "file": result["parameters"]["args"]["file_name"],
                "correct": result["result"]["correct"],
                "args": result["parameters"]["args"]["parameter"].get("args", None),
                "evaluation": result["result"]["evaluation"],
                "timeout": result["parameters"]["args"]["parameter"]["timeout"],
                # "runtime": result["runtime"],
                "runtime": result["result"]["time_solver"],
                "pre_time": result["result"]["time_pre_solver"],
                "solution": result["result"].get("solution", None),
            },
        )
        # Filter nach Host, falls host angegeben ist
        table = table[table["host"].isin(self.host)]

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

        table = table[table["solver"].isin(self.solvers_name)]
        return table

    def applay_instanze(
        self,
        table: pd.DataFrame,
    ) -> pd.DataFrame:
        # Kombiniere Instanz und Dateiname für die x-Achse
        table["instance_file"] = table["instance"] + "/" + table["file"]
        return table

    def apply_args(self, table: pd.DataFrame) -> pd.DataFrame:
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
            raise ValueError("Keine Daten für die angegebene Konfiguration gefunden.")

        # Create mapping from unique args to numbers, grouped by solver
        solver_args_mapping = {}
        solver_args_multiple = {}
        for solver in self.solvers_name:
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

        table = table.sort_values(by=["host", "solver_args"])

        if table.empty:
            raise ValueError("Keine Daten für die angegebene Konfiguration gefunden.")

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
        if self.name:
            if not os.path.exists(self.figure_path):
                os.makedirs(self.figure_path)
            with open(os.path.join(self.figure_path, f"{self.name}.txt"), "w") as f:
                f.write(legend)
        logging.info(legend)
        return table

    def show(
        self,
        timelimit: int = 300,
        block: bool = True,
    ):
        table = self.get_table()
        table = self.applay_instanze(table)
        table = self.apply_args(table)

        table["total_runtime"] = table["pre_time"] + table["runtime"]
        self.create_cactus(
            table=table,
            y="total_runtime",
            block=block,
            timelimit=timelimit,
        )

    def create_cactus(
        self,
        table,
        y: str,
        block: bool = False,
        timelimit: int = 300,
    ):
        """
        Erstellt einen Cactus Plot für die Benchmark-Daten.
        In einem Cactus Plot wird die Zeit (y-Achse) gegen die Anzahl der gelösten
        Instanzen (x-Achse) dargestellt, sortiert nach Laufzeit.
        """
        # Seaborn Style setzen
        sns.set_style("whitegrid")

        # Filter gültige Werte (entferne negative Werte wie -1 für Timeouts)
        valid_data = table[table[y] >= 0].copy()

        if len(valid_data) == 0:
            logging.warning(f"Keine gültigen Daten für {y} Cactus Plot gefunden")
            return

        # Eindeutige Solver und Instanzen ermitteln
        unique_solvers = valid_data["solver_args"].unique()
        unique_instances = valid_data["instance"].unique()

        # Bessere Farbpalette für Solver - verschiedene Optionen je nach Anzahl
        n_solvers = len(unique_solvers)

        if n_solvers <= 8:
            # Für wenige Solver: ColorBrewer Dark2 (sehr gut unterscheidbar)
            colors = sns.color_palette("Dark2", n_solvers)
        elif n_solvers <= 10:
            # Für mittlere Anzahl: tab10 (matplotlib standard, gut unterscheidbar)
            colors = sns.color_palette("tab10", n_solvers)
        elif n_solvers <= 12:
            # Für mehr Solver: Set3 (12 helle, unterscheidbare Farben)
            colors = sns.color_palette("Set3", n_solvers)
        elif n_solvers <= 20:
            # Für viele Solver: tab20 (20 verschiedene Farben)
            colors = sns.color_palette("tab20", n_solvers)
        elif n_solvers <= 40:
            # Für sehr viele Solver: tab20 + tab20b kombiniert (40 Farben)
            colors1 = sns.color_palette("tab20", 20)
            colors2 = sns.color_palette("tab20b", n_solvers - 20)
            colors = colors1 + colors2
        else:
            # Für extrem viele Solver: husl (unbegrenzt, gleichmäßig verteilt)
            colors = sns.color_palette("husl", n_solvers)

        # Bestimme Layout für Subplots
        n_instances = len(unique_instances)
        cols = min(3, n_instances)  # Maximal 3 Spalten
        rows = (n_instances + cols - 1) // cols  # Aufrunden

        fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows))

        # Für den Fall dass nur eine Instanz vorhanden ist
        if n_instances == 1:
            axes = [axes]
        elif rows == 1:
            axes = axes if isinstance(axes, (list, np.ndarray)) else [axes]
        else:
            axes = axes.flatten()

        # Für jede Instanz einen eigenen Plot
        for idx, instance in enumerate(unique_instances):
            ax = axes[idx]
            len_instance = len(self.instances[instance])

            # Für jeden Solver in dieser Instanz plotten
            for i, solver in enumerate(unique_solvers):
                instance_solver_data = valid_data[
                    (valid_data["solver_args"] == solver)
                    & (valid_data["instance"] == instance)
                ][y].values

                if len(instance_solver_data) == 0:
                    continue

                # Sortieren für Cactus Plot (wichtig!)
                times_sorted = np.sort(instance_solver_data)
                y_values = np.arange(1, len(times_sorted) + 1)

                # Punkt (0,0) hinzufügen - bei Zeit 0 sind 0 Instanzen gelöst
                times_with_zero = np.concatenate([[0], times_sorted])
                y_values_with_zero = np.concatenate([[0], y_values])

                # Y-Werte in Prozent umwandeln
                y_values_percent = (y_values_with_zero / len_instance) * 100

                # Füge einen Punkt beim Timelimit hinzu, falls die Linie nicht bis dahin reicht
                if len(times_with_zero) > 1 and times_with_zero[-1] < timelimit:
                    # Aktueller y-Wert (Prozentsatz der gelösten Instanzen) bleibt beim Timelimit
                    times_with_timelimit = np.concatenate(
                        [times_with_zero, [timelimit]]
                    )
                    y_values_with_timelimit = np.concatenate(
                        [y_values_percent, [y_values_percent[-1]]]
                    )
                else:
                    times_with_timelimit = times_with_zero
                    y_values_with_timelimit = y_values_percent

                ax.plot(
                    times_with_timelimit,
                    y_values_with_timelimit,
                    "o-",
                    color=colors[i],
                    label=solver,
                    linewidth=2,
                    markersize=3,
                    alpha=0.8,
                    drawstyle="steps-post",
                )

            # Subplot Styling
            ax.set_xlabel(f"{y.replace('_', ' ').title()} (Sekunden)", fontsize=10)
            ax.set_ylabel("Gelöste Instanzen (%)", fontsize=10)
            ax.set_title(f"{instance}", fontsize=12, fontweight="bold")
            ax.grid(True, alpha=0.3, linestyle="-", linewidth=0.5)

            # Y-Achse auf 0-105% setzen, damit 100%-Linie und Beschriftung sichtbar sind
            ax.set_ylim(0, 105)

            # Horizontale Linie bei 100% hinzufügen
            ax.axhline(
                y=100,
                color="green",
                linestyle="-",
                alpha=0.6,
                linewidth=1.5,
            )

            # Beschriftung für die 100% Linie
            ax.text(
                ax.get_xlim()[1] * 0.5,
                101,
                "100% gelöst",
                verticalalignment="bottom",
                horizontalalignment="center",
                fontsize=8,
                color="green",
                alpha=0.8,
            )

            # Vertikale Linie bei timelimit hinzufügen
            ax.axvline(
                x=timelimit,
                color="red",
                linestyle="--",
                alpha=0.7,
                linewidth=1.5,
            )

            # Beschriftung direkt an die Linie
            ax.text(
                timelimit + 12,
                50,
                f"Timelimit ({timelimit}s)",
                rotation=90,
                verticalalignment="center",
                horizontalalignment="right",
                fontsize=8,
                color="red",
                alpha=0.8,
            )

        # Verstecke überschüssige Subplots
        for idx in range(n_instances, len(axes)):
            axes[idx].set_visible(False)

        # Gesamttitel
        fig.suptitle(
            f"Cactus Plot - {y.replace('_', ' ').title()} Performance Vergleich",
            fontsize=16,
            fontweight="bold",
        )

        # Legende im freien Bereich unten rechts mit mehreren Spalten
        handles, labels = axes[0].get_legend_handles_labels()
        if handles:
            # Berechne Anzahl Spalten basierend auf Anzahl der Solver
            n_cols = min(3, len(handles))  # Maximal 3 Spalten
            fig.legend(
                handles,
                labels,
                loc="lower right",
                bbox_to_anchor=(0.94, 0.26),
                ncol=n_cols,
                fontsize=9,
                frameon=True,
                fancybox=True,
                shadow=True,
            )

        # Layout optimieren
        fig.tight_layout()

        fig_name = self.name if self.name else f"cactus_{y}"
        # Speichern falls Pfad angegeben
        if self.figure_path:
            fig.savefig(
                os.path.join(self.figure_path, f"{fig_name}.pdf"),
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

    def add_entrys(
        self,
        key: str,
        number_runs: int = NUMBER_RUNS_FOR_AVG,
    ):
        solver, nodes, possible, inst, file_name = self.get_solver_inst_from_runlist[
            key
        ]
        parameters = self.outer_parameter[solver]
        for parameter in parameters:
            for _ in range(number_runs):
                run_seed = int(uuid.uuid4())
                random.seed(run_seed)  # Seed für Reproduzierbarkeit
                random.shuffle(nodes)  # Zufällige Reihenfolge der Knoten
                graph = Graph_Wrapper(nodes)

                self.benchmark.add(
                    self.create_benchmark_entry,
                    solver_name=solver.NAME,
                    parameter=parameter,
                    instance_name=inst,
                    file_name=file_name,
                    run_seed=run_seed,
                    _possible=possible,
                    _solver_type=solver,
                    _graph=graph,
                )

    @staticmethod
    def create_benchmark_entry(
        solver_name: str,
        parameter: dict,
        instance_name: str,
        file_name: str,
        run_seed: int,
        _possible: bool,
        _solver_type: type[Solver],
        _graph: Graph_Wrapper,
    ):
        info = ""
        try:
            solver = _solver_type(_graph)
            solver.logger.info(f"Running {solver.name} on {instance_name}_{file_name}")
            solution: dict = solver.solve(parameter)
        except Exception as e:
            info += f"Error while solving: {e}\n"
            solver.logger.info(f"Error while solving: {e}")
            return {
                "correct": False,
                "time_solver": -1,
                "time_pre_solver": -1,
                "evaluation": 0.0,
                "triangulation": [],
                "info": info,
                "solution": {},
                "big_error": True,
            }

        is_triangulation = _graph.check_if_triangulation_with_degree_constrained()
        result = solution["success"] and is_triangulation
        correct = _possible == result
        big_error = False
        if is_triangulation and not _possible:
            info += f"{solver.name} on {instance_name}_{file_name} should not be possible, but triangulation was found.\n"
            big_error = True

        solver.logger.info(f"Finished with: {correct}")
        if big_error:
            solver.logger.error(
                f"{solver.name} on {instance_name}_{file_name} should not be possible, but triangulation was found.\n"
            )
        return {
            "correct": correct,
            "time_pre_solver": solver.pre_solve_time,
            "time_solver": solver.solve_time,
            "timing": solver.timing,
            "evaluation": _graph.evaluate(),
            "triangulation": _graph.get_all_edges(True),
            "info": info,
            "solution": solution,
            "big_error": big_error,
        }

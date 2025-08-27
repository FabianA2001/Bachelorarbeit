import logging
import os
from collections import defaultdict
from dataclasses import asdict

from dc_triangulation import (
    SAT,
    Gurobi,
    Gurobi_Parameter,
    Ortools,
    Ortools_Parameter,
    Run_Algbench,
    SAT_Parameter,
    format_dictionary,
)

TIMEOUT = 300
path = os.path.join(os.path.dirname(__file__), "instances")
figure_path = os.path.join(os.path.dirname(__file__), "figures")
HOST = ["algra01", "algra02", "algra03", "algra04", "algra05", "algra06"]
NUMBER_RUNS = 5
benchmark_path = os.path.join(os.path.dirname(__file__), "lokal_benchmark")


def show_sat():
    outer_parameter = defaultdict(list)
    for i in range(NUMBER_RUNS):
        sat_args = asdict(
            SAT_Parameter(intersection=True, degree_exact=True, run_num=i)
        )
        outer_parameter[SAT].append({"timeout": TIMEOUT, "args": sat_args})

    ri = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        host=HOST,
        name="sat",
        path_benchmark=benchmark_path,
    )
    ri.show(block=False)


def show_ortools():
    outer_parameter = defaultdict(list)
    for i in range(NUMBER_RUNS):
        ortools_args = asdict(
            Ortools_Parameter(intersection=True, degree=True, run_num=i)
        )
        outer_parameter[Ortools].append({"timeout": TIMEOUT, "args": ortools_args})

    ri = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        host=HOST,
        name="ortools",
        path_benchmark=benchmark_path,
    )
    # ri.show(block=False)
    ########### hack ######################

    table = ri.get_table()
    table = ri.apply_instance(table)
    all_args = []
    for arg_list in ri.outer_parameter.values():
        for arg in arg_list:
            arg = arg["args"]
            del arg["save_state_after_solution"]
            print(arg)
            all_args.append(arg)

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
    for solver in ri.solvers_name:
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
    if ri.name:
        if not os.path.exists(ri.figure_path):
            os.makedirs(ri.figure_path)
        with open(os.path.join(ri.figure_path, f"{ri.name}.txt"), "w") as f:
            f.write(legend)
    logging.info(legend)

    table["total_runtime"] = table["pre_time"] + table["runtime"]
    ri.create_cactus(
        table=table,
        y="total_runtime",
        block=False,
        timelimit=TIMEOUT,
    )
    #######################################


def show_gurobi():
    outer_parameter = defaultdict(list)
    for i in range(NUMBER_RUNS):
        gurobi_args = asdict(
            Gurobi_Parameter(intersection=True, degree=True, run_num=i)
        )
        outer_parameter[Gurobi].append({"timeout": TIMEOUT, "args": gurobi_args})

    ri = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        host=HOST,
        name="gurobi",
        path_benchmark=benchmark_path,
    )
    ri.show(block=False)


if __name__ == "__main__":
    show_sat()
    show_gurobi()
    show_ortools()

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
)

TIMEOUT = 300
path = os.path.join(os.path.dirname(__file__), "instances")
figure_path = os.path.join(os.path.dirname(__file__), "figures")
HOST = ["algry01", "algry02", "algry03", "algry04"]
NUMBER_RUNS = 5


def show_sat():
    outer_parameter = defaultdict(list)
    for i in range(NUMBER_RUNS):
        sat_args = asdict(SAT_Parameter(intersection=True, degree_exact=True))
        sat_args["version"] = i
        outer_parameter[SAT].append({"timeout": TIMEOUT, "args": sat_args})

    ri = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        host=HOST,
        name="tri",
    )
    ri.show(block=False)


def show_ortools():
    outer_parameter = defaultdict(list)
    for i in range(NUMBER_RUNS):
        ortools_args = asdict(Ortools_Parameter(intersection=True, degree=True))
        ortools_args["version"] = i
        outer_parameter[Ortools].append({"timeout": TIMEOUT, "args": ortools_args})

    ri = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        host=HOST,
        name="tri",
    )
    ri.show(block=False)


def show_gurobi():
    outer_parameter = defaultdict(list)
    for i in range(NUMBER_RUNS):
        gurobi_args = asdict(Gurobi_Parameter(intersection=True, degree=True))
        gurobi_args["version"] = i
        outer_parameter[Gurobi].append({"timeout": TIMEOUT, "args": gurobi_args})

    ri = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        host=HOST,
        name="tri",
    )
    ri.show(block=False)


if __name__ == "__main__":
    show_sat()
    show_gurobi()
    show_ortools()

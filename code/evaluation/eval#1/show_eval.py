import os
from dataclasses import asdict

from dc_triangulation import (
    SAT,
    SAT_TRI,
    Gurobi,
    Gurobi_Parameter,
    Gurobi_Tri,
    Gurobi_Tri_Parameter,
    Ortools,
    Ortools_Parameter,
    OrTools_Tri,
    Ortools_Tri_Parameter,
    Run_Algbench,
    SAT_Parameter,
    SAT_Tri_Parameter,
)

TIMEOUT = 300
path = os.path.join(os.path.dirname(__file__), "instances")
figure_path = os.path.join(os.path.dirname(__file__), "figures")
HOST = ["algry01", "algry02", "algry03", "algry04"]


def show_tri():
    outer_parameter = {
        Gurobi_Tri: [
            {
                "timeout": TIMEOUT,
                "args": asdict(Gurobi_Tri_Parameter(intersection=True, degree=True)),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    Gurobi_Tri_Parameter(
                        intersection=True, degree=True, exclude_edges=True
                    )
                ),
            },
        ],
        OrTools_Tri: [
            {
                "timeout": TIMEOUT,
                "args": asdict(Ortools_Tri_Parameter(intersection=True, degree=True)),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    Ortools_Tri_Parameter(
                        intersection=True, degree=True, exclude_edges=True
                    )
                ),
            },
        ],
        SAT_TRI: [
            {
                "timeout": TIMEOUT,
                "args": asdict(SAT_Tri_Parameter(intersection=True, degree=True)),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Tri_Parameter(
                        intersection=True, degree=True, exclude_edges=True
                    )
                ),
            },
        ],
    }

    ri = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        host=HOST,
        name="tri",
    )
    ri.show(block=False)


def show_sat():
    outer_parameter = {
        SAT: [
            {
                "timeout": TIMEOUT,
                "args": asdict(SAT_Parameter(intersection=True, degree_exact=True)),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(intersection=True, degree_exact=True, fix_hull=True)
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True,
                        degree_exact=True,
                        all_edges=True,
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True,
                        degree_exact=True,
                        exclude_edges=True,
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(intersection=True, degree_exact=True, fix_edges=True)
                ),
            },
        ],
    }

    ri = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        host=HOST,
        name="sat",
    )
    ri.show(block=False)


def show_gurobi():
    outer_parameter = {
        Gurobi: [
            {
                "timeout": TIMEOUT,
                "args": asdict(Gurobi_Parameter(intersection=True, degree=True)),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    Gurobi_Parameter(intersection=True, degree=True, fix_hull=True)
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    Gurobi_Parameter(intersection=True, degree=True, all_edges=True)
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    Gurobi_Parameter(intersection=True, degree=True, exclude_edges=True)
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    Gurobi_Parameter(intersection=True, degree=True, fix_edges=True)
                ),
            },
        ],
    }

    ri = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        host=HOST,
        name="gurobi",
    )
    ri.show(block=False)


def show_ortools():
    outer_parameter = {
        Ortools: [
            {
                "timeout": TIMEOUT,
                "args": asdict(Ortools_Parameter(intersection=True, degree=True)),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    Ortools_Parameter(intersection=True, degree=True, fix_hull=True)
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    Ortools_Parameter(intersection=True, degree=True, all_edges=True)
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    Ortools_Parameter(
                        intersection=True,
                        degree=True,
                        exclude_edges=True,
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    Ortools_Parameter(intersection=True, degree=True, fix_edges=True)
                ),
            },
        ],
    }

    ri = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        host=HOST,
        name="ortools",
    )
    ri.show(block=False)


if __name__ == "__main__":
    show_tri()
    show_sat()
    show_gurobi()
    show_ortools()

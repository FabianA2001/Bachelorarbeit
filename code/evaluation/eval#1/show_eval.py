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

    arg_names = {
        "gurobi_tri": ["normal", "Kanten ausschließen"],
        "OrTools_tri": ["normal", "Kanten ausschließen"],
        "SAT_TRI": ["normal", "Kanten ausschließen"],
    }

    ri = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        host=HOST,
        name="tri",
        arg_names=arg_names,
    )
    ri.show(block=False)


def show_sat():
    outer_parameter = {
        SAT: [
            {
                "timeout": TIMEOUT,
                "args": asdict(SAT_Parameter(intersection=True, degree_atleast=True)),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(intersection=True, degree_atleast=True, fix_hull=True)
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True,
                        degree_atleast=True,
                        all_edges=True,
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True,
                        degree_atleast=True,
                        exclude_edges=True,
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True, degree_atleast=True, fix_edges=True
                    )
                ),
            },
        ],
    }

    arg_names = {
        "SAT": [
            "alternative Kanten",
            "normal",
            "Hülle fixieren",
            "Kanten ausschließen",
            "Kanten fixieren",
        ]
    }

    ri = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        host=HOST,
        name="sat",
        arg_names=arg_names,
        show_solver_in_legend=False,
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
    arg_names = {
        "gurobi": [
            "Kanten fixieren",
            "normal",
            "Hülle fixieren",
            "alternative Kanten",
            "Kanten ausschließen",
        ]
    }
    ri = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        host=HOST,
        name="gurobi",
        show_solver_in_legend=False,
        arg_names=arg_names,
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
        ]
    }

    arg_names = {
        "Ortools": [
            "normal",
            "Hülle fixieren",
            "alternative Kanten",
            "Kanten ausschließen",
            "Kanten fixieren",
        ]
    }

    ri = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        host=HOST,
        name="ortools",
        show_solver_in_legend=False,
        arg_names=arg_names,
    )
    ri.show(block=False)


def gesamt():
    outer_parameter = {
        SAT: [
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True, degree_atleast=True, fix_edges=True
                    )
                ),
            }
        ],
        Gurobi: [
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    Gurobi_Parameter(intersection=True, degree=True, fix_edges=True)
                ),
            },
        ],
        Ortools: [
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    Ortools_Parameter(intersection=True, degree=True, fix_edges=True)
                ),
            }
        ],
        Gurobi_Tri: [
            {
                "timeout": TIMEOUT,
                "args": asdict(Gurobi_Tri_Parameter(intersection=True, degree=True)),
            }
        ],
        OrTools_Tri: [
            {
                "timeout": TIMEOUT,
                "args": asdict(Ortools_Tri_Parameter(intersection=True, degree=True)),
            }
        ],
        SAT_TRI: [
            {
                "timeout": TIMEOUT,
                "args": asdict(SAT_Tri_Parameter(intersection=True, degree=True)),
            }
        ],
    }

    ri = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        host=HOST,
        name="gesamt",
    )
    ri.show(block=False)


if __name__ == "__main__":
    # show_sat()
    # show_gurobi()
    # show_ortools()
    # gesamt()
    show_tri()

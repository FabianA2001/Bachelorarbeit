import os
from dataclasses import asdict

from dc_triangulation import (
    SAT,
    SAT_TRI,
    Delaunay,
    Gurobi,
    Gurobi_Parameter,
    Gurobi_Tri,
    Gurobi_Tri_Parameter,
    Iterative,
    Ortools,
    Ortools_Parameter,
    Random_Adder,
    Raw_Flips,
    Run_Algbench,
    SAT_Parameter,
    SAT_Tri_Parameter,
)

asdict
if __name__ == "__main__":
    TIMEOUT = 300
    path = os.path.join(os.path.dirname(__file__), "instances")
    # This is the entry point for the evaluation script
    # It will run the Run_Instance class from run_algbench module
    outer_parameter = {
        SAT: [
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True,
                        degree_exact=True,
                        fix_hull=True,
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
                        fix_hull=True,
                        all_edges=True,
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True,
                        degree_subset=True,
                        fix_hull=True,
                        all_edges=True,
                    )
                ),
            },
        ]
    }

ri = Run_Algbench(
    inst_path=path,
    outer_parameter=outer_parameter,
    figure_path=os.path.dirname(__file__),
)
ri.run()
ri.show()


def get_solvers():
    return [
        Raw_Flips,
        Delaunay,
        Iterative,
        Ortools,
        SAT,
        Random_Adder,
        SAT_TRI,
        Gurobi_Tri,
        Gurobi,
    ]


def get_parameters():
    return [
        SAT_Parameter,
        Ortools_Parameter,
        SAT_Tri_Parameter,
        Gurobi_Tri_Parameter,
        Gurobi_Parameter,
    ]

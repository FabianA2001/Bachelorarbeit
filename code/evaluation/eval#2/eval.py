import os
from dataclasses import asdict

from dc_triangulation import (
    SAT,
    SAT_TRI,
    Gurobi,
    Gurobi_Parameter,
    Ortools,
    Ortools_Parameter,
    Run_Algbench,
    SAT_Parameter,
    SAT_TRI_Parameter,
)

if __name__ == "__main__":
    path = os.path.join(os.path.dirname(__file__), "instances")
    # This is the entry point for the evaluation script
    # It will run the Run_Instance class from run_algbench module
    outer_parameter = {
        SAT: [
            {
                "timeout": -1,
                "args": asdict(
                    SAT_Parameter(intersection=True, degree_exact=True, fix_hull=True)
                ),
            },
        ],
        Ortools: [
            {
                "timeout": -1,
                "args": asdict(Ortools_Parameter(intersection=True, degree=True)),
            },
        ],
        Gurobi: [
            {
                "timeout": -1,
                "args": asdict(Gurobi_Parameter(intersection=True, degree=True)),
            },
        ],
        SAT_TRI: [
            {
                "timeout": -1,
                "args": asdict(SAT_TRI_Parameter(intersection=True, degree=True)),
            },
        ],
    }

    ri = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        ignore_correct=True,
        figure_path=os.path.dirname(__file__),
    )
    ri.run()
    ri.show()

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
    Run_Algbench,
    SAT_Parameter,
    SAT_Tri_Parameter,
)

if __name__ == "__main__":
    TIMEOUT = 300
    path = os.path.join(os.path.dirname(__file__), "instances")
    # This is the entry point for the evaluation script
    # It will run the Run_Instance class from run_algbench module
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
                        exclude_edges=True,
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True,
                        degree_exact=True,
                        add_allEdges_or_exclude_edges=False,
                    )
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
        ],
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
        ],
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
                    Gurobi_Parameter(intersection=True, degree=True, exclude_edges=True)
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    Gurobi_Parameter(intersection=True, degree=True, all_edges=True)
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
        figure_path=os.path.dirname(__file__),
    )
    ri.run()
    ri.show()

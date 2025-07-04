import os
from dataclasses import asdict

from dc_triangulation import (
    SAT,
    SAT_TRI,
    Graph_Wrapper,
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
                Gurobi_Tri_Parameter(intersection=True, degree=True, exclude_edges=True)
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
                SAT_Tri_Parameter(intersection=True, degree=True, exclude_edges=True)
            ),
        },
    ],
}

RI = Run_Algbench(
    inst_path=path,
    outer_parameter=outer_parameter,
    figure_path=os.path.dirname(__file__),
)


def run_solver_on_inst(key: str):
    solver, nodes, possible, inst, file_name = RI.get_solver_inst_from_runlist[key]
    parameters = RI.outer_parameter[solver]
    for parameter in parameters:
        graph = Graph_Wrapper(nodes)
        RI.benchmark.add(
            RI.create_benchmark_entry,
            solver_name=solver.NAME,
            parameter=parameter,
            instance_name=inst,
            file_name=file_name,
            _possible=possible,
            _solver_type=solver,
            _graph=graph,
        )


if __name__ == "__main__":
    run_list = RI.get_run_list()
    for key in run_list:
        run_solver_on_inst(key)
    RI.compress()
    RI.show()

import os
from dataclasses import asdict

from dc_triangulation import (
    SAT,
    Graph_Wrapper,
    Gurobi,
    Gurobi_Parameter,
    Run_Algbench,
    SAT_Parameter,
)

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
        {
            "timeout": -1,
            "args": asdict(SAT_Parameter(intersection=True, degree_exact=True)),
        },
    ],
    Gurobi: [
        {
            "timeout": -1,
            "args": asdict(
                Gurobi_Parameter(intersection=True, degree=True, fix_hull=True)
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

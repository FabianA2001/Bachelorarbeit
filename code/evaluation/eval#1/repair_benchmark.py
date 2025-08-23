import os
from dataclasses import asdict

import algbench
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

bench = os.path.join(os.path.dirname(__file__), "..", "benchmark")
fehlerhafte_bench = os.path.join(
    os.path.dirname(__file__), "..", "benchmark_fehlerhaft"
)

TIMEOUT = 300
path = os.path.join(os.path.dirname(__file__), "instances")
# This is the entry point for the evaluation script
# It will run the Run_Instance class from run_algbench module
outer_parameter = {
    SAT: [
        {
            "timeout": TIMEOUT,
            "args": asdict(
                SAT_Parameter(intersection=True, degree_atleast=True, fix_edges=True)
            ),
        },
    ],
    Ortools: [
        {
            "timeout": TIMEOUT,
            "args": asdict(
                Ortools_Parameter(intersection=True, degree=True, fix_edges=True)
            ),
        },
    ],
    Gurobi: [
        {
            "timeout": TIMEOUT,
            "args": asdict(
                Gurobi_Parameter(intersection=True, degree=True, fix_edges=True)
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
                SAT_Tri_Parameter(intersection=True, degree=True, exclude_edges=True)
            ),
        },
    ],
}

RI = Run_Algbench(
    inst_path=path,
    outer_parameter=outer_parameter,
    figure_path=os.path.dirname(__file__),
    host=["algry01", "algry02", "algry03", "algry04"],
)

if __name__ == "__main__":
    alg_error = algbench.Benchmark(fehlerhafte_bench)
    alg = algbench.Benchmark(bench)
    alg.compress()

    # add_list = []
    # for (
    #     solver,
    #     nodes,
    #     possible,
    #     inst,
    #     file_name,
    # ) in RI.get_solver_inst_from_runlist.values():
    #     parameters = RI.outer_parameter[solver]
    #     for para in parameters:
    #         add_list.append(
    #             (
    #                 solver.NAME,
    #                 inst,
    #                 file_name,
    #                 para["args"],
    #             )
    #         )
    # for dictionary in alg_error:
    #     try:
    #         if (
    #             dictionary["parameters"]["args"]["solver_name"],
    #             dictionary["parameters"]["args"]["instance_name"],
    #             dictionary["parameters"]["args"]["file_name"],
    #             dictionary["parameters"]["args"]["parameter"]["args"],
    #         ) in add_list and dictionary["env"]["hostname"] in RI.host:
    #             print("insert")
    #             alg.insert(dictionary)
    #     except KeyError:
    #         pass

import os
from dataclasses import asdict

import slurminade
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
# This is the entry point for the evaluation script
# It will run the Run_Instance class from run_algbench module
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
                SAT_Parameter(intersection=True, degree_atleast=True, fix_edges=True)
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


@slurminade.slurmify()
def run_solver_on_inst(key: str):
    RI.add_entrys(key)


@slurminade.slurmify(mail_type="ALL")
def compress_results():
    # Compress the results to save significant disk space
    RI.compress()


if __name__ == "__main__":
    if True:
        slurminade.update_default_configuration(
            # Your supervisor will tell you these details
            partition="alg",  # Which partition to use. Usually group name.
            constraint="alggen03",  # Which workstations within the partition to use
            exclusive=True,  # To use all cores on a node exclusively
            mail_type="FAIL",  # Send mail on failure
            mail_user="f.alich@tu-braunschweig.de",  # Mail to this address
        )
        run_list = RI.get_run_list()
        with slurminade.JobBundling(max_size=7):
            for key in run_list:
                run_solver_on_inst.distribute(key)

        slurminade.join()
        compress_results.distribute()
    else:
        # for key in RI.get_run_list():
        #     RI.delete_key_from_runlist(key)
        #     # RI.show_key_from_runlist(key)
        # RI.delete_runlist()
        RI.show()
        # counter = 0
        # for key in RI.get_run_list():
        #     counter += 1
        #     solver, nodes, possible, inst, file_name = RI.get_solver_inst_from_runlist[
        #         key
        #     ]
        #     if solver.NAME != "SAT":
        #         continue
        #     if "iterative" not in inst:
        #         continue
        #     RI.show_key_from_runlist(key, check_correct=True)

        # print(f"Total entries in run list: {counter}")

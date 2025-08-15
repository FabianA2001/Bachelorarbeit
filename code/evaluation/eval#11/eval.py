import os
from dataclasses import asdict

import slurminade
from dc_triangulation import (
    Ortools,
    Ortools_Parameter,
    Run_Algbench,
)

TIMEOUT = 300
path = os.path.join(os.path.dirname(__file__), "instances")
# This is the entry point for the evaluation script
# It will run the Run_Instance class from run_algbench module
outer_parameter = {
    Ortools: [
        {
            "timeout": TIMEOUT,
            "args": asdict(
                Ortools_Parameter(
                    intersection=True,
                    all_edges=True,
                    fix_hull=True,
                    evaluation_direction=True,
                    save_state_after_solution=True,
                )
            ),
        },
        {
            "timeout": TIMEOUT,
            "args": asdict(
                Ortools_Parameter(
                    intersection=True,
                    all_edges=True,
                    fix_hull=True,
                    min_max_direction=True,
                    save_state_after_solution=True,
                )
            ),
        },
    ]
}


RI = Run_Algbench(
    inst_path=path,
    outer_parameter=outer_parameter,
    figure_path=os.path.dirname(__file__),
    # host=["algry01", "algry02", "algry03", "algry04"],
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
            constraint="alggen02",  # Which workstations within the partition to use
            exclusive=True,  # To use all cores on a node exclusively
            mail_type="FAIL",  # Send mail on failure
            mail_user="f.alich@tu-braunschweig.de",  # Mail to this address
        )
        # run_list = RI.get_run_list()
        # with slurminade.JobBundling(max_size=10):
        #     for key in run_list:
        #         run_solver_on_inst.distribute(key)

        slurminade.join()
        compress_results.distribute()
    else:
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

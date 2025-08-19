import os
from dataclasses import asdict

import slurminade
from dc_triangulation import (
    Ortools,
    Ortools_Parameter,
    Run_Algbench,
)

TIMEOUT = 1800  # 30 minutes in seconds
path = os.path.join(os.path.dirname(__file__), "instances")
# This is the entry point for the evaluation script
# It will run the Run_Instance class from run_algbench module
outer_parameter = {
    Ortools: [
        {
            "timeout": TIMEOUT,
            "args": asdict(
                Ortools_Parameter(
                    intersection=True, degree=True, fix_hull=True, all_edges=True
                )
            ),
        },
    ],
}

RI = Run_Algbench(
    inst_path=path,
    outer_parameter=outer_parameter,
    figure_path=os.path.dirname(__file__),
    host=["algra01", "algra02", "algra03", "algra04", "algra05", "algra06"],
)


@slurminade.slurmify()
def run_solver_on_inst(key: str):
    RI.add_entrys(key)


@slurminade.slurmify(mail_type="ALL")
def compress_results():
    # Compress the results to save significant disk space
    RI.compress()


if __name__ == "__main__":
    if False:
        slurminade.update_default_configuration(
            # Your supervisor will tell you these details
            partition="alg",  # Which partition to use. Usually group name.
            constraint="alggen04",  # Which workstations within the partition to use
            exclusive=True,  # To use all cores on a node exclusively
            mail_type="FAIL",  # Send mail on failure
            mail_user="f.alich@tu-braunschweig.de",  # Mail to this address
        )
        run_list = RI.get_run_list()
        with slurminade.JobBundling(max_size=10):
            for key in run_list:
                run_solver_on_inst.distribute(key)

        slurminade.join()
        compress_results.distribute()
    else:
        RI.show()

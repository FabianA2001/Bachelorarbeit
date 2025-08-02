import os
from dataclasses import asdict

import slurminade
from dc_triangulation import (
    SAT,
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
        #     {
        #         "timeout": -1,
        #         "args": asdict(SAT_Parameter(intersection=True, degree_exact=True)),
        #     },
    ],
    # Gurobi: [
    #     {
    #         "timeout": -1,
    #         "args": asdict(
    #             Gurobi_Parameter(intersection=True, degree=True, fix_hull=True)
    #         ),
    #     },
    # ],
}

RI = Run_Algbench(
    inst_path=path,
    outer_parameter=outer_parameter,
    figure_path=os.path.dirname(__file__),
    ignore_correct=True,
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
        for key in run_list:
            run_solver_on_inst.distribute(key)

        slurminade.join()
        compress_results.distribute()
    else:
        # RI.delete_runlist()
        # for key in RI.get_run_list():
        # RI.show_key_from_runlist(key)
        RI.show()
        # print(len(list(RI.benchmark)))

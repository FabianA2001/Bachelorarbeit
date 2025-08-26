import os
from dataclasses import asdict

import slurminade
from dc_triangulation import Cadical, Cadical_Parameter, Run_Algbench

TIMEOUT = 300
path = os.path.join(os.path.dirname(__file__), "instances")
lokal_benchmark = os.path.join(os.path.dirname(__file__), "lokal_benchmark")
# This is the entry point for the evaluation script
# It will run the Run_Instance class from run_algbench module
outer_parameter = {
    Cadical: [
        {
            "timeout": TIMEOUT,
            "args": asdict(
                Cadical_Parameter(
                    degree=True,
                    intersection=True,
                    fix_hull=True,
                    # save_state=True,
                    optimize_propagation=True,
                    exclude_edges=True,
                )
            ),
        },
    ]
}

RI = Run_Algbench(
    inst_path=path,
    outer_parameter=outer_parameter,
    figure_path=os.path.dirname(__file__),
    path_benchmark=lokal_benchmark,
    # host=["algry01", "algry02", "algry03", "algry04"],
)


@slurminade.slurmify()
def run_solver_on_inst(key: str):
    RI.add_entrys(key, 1)


@slurminade.slurmify(mail_type="ALL")
def compress_results():
    # Compress the results to save significant disk space
    RI.compress()


if __name__ == "__main__":
    slurminade.update_default_configuration(
        # Your supervisor will tell you these details
        partition="alg",  # Which partition to use. Usually group name.
        constraint="alggen02",  # Which workstations within the partition to use
        exclusive=True,  # To use all cores on a node exclusively
        mail_type="FAIL",  # Send mail on failure
        mail_user="f.alich@tu-braunschweig.de",  # Mail to this address
    )
    # run_list = RI.get_run_list()
    # # with slurminade.JobBundling(max_size=3):
    # for key in run_list:
    #     run_solver_on_inst.distribute(key)

    slurminade.join()
    compress_results.distribute()

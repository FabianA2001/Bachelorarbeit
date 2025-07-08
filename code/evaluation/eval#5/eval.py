import os
from dataclasses import asdict

import slurminade
from dc_triangulation import SAT, Graph_Wrapper, Run_Algbench, SAT_Parameter

asdict
if __name__ == "__main__":
    TIMEOUT = 300
    path = os.path.join(os.path.dirname(__file__), "instances")
    # This is the entry point for the evaluation script
    # It will run the Run_Instance class from run_algbench module
    outer_parameter = {
        SAT: [
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True,
                        degree_exact=True,
                        fix_hull=True,
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
                        fix_hull=True,
                        all_edges=True,
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True,
                        degree_subset=True,
                        fix_hull=True,
                        all_edges=True,
                    )
                ),
            },
        ]
    }


RI = Run_Algbench(
    inst_path=path,
    outer_parameter=outer_parameter,
    figure_path=os.path.dirname(__file__),
)


@slurminade.node_setup
def configure_grb_license_path():
    # copy and paste solution for handling Gurobi licenses.
    import socket
    from pathlib import Path

    if "alg" not in socket.gethostname():
        return

    # TODO: Make sure that the license file is in the correct location
    # It is expected that the license file is in the following location:
    # ~/.gurobi/{$HOSTNAME}/gurobi.lic
    # You can of course change this path to whatever you like.
    grb_license_path = Path.home() / ".gurobi" / socket.gethostname() / "gurobi.lic"
    import os

    os.environ["GRB_LICENSE_FILE"] = str(grb_license_path)

    if not grb_license_path.exists():
        msg = "Gurobi License File does not exist."
        raise RuntimeError(msg)


@slurminade.slurmify()
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


@slurminade.slurmify(mail_type="ALL")
def compress_results():
    # Compress the results to save significant disk space
    RI.compress()


if __name__ == "__main__":
    if True:
        slurminade.update_default_configuration(
            # Your supervisor will tell you these details
            partition="alg",  # Which partition to use. Usually group name.
            constraint="alggen05",  # Which workstations within the partition to use
            exclusive=True,  # To use all cores on a node exclusively
            mail_type="FAIL",  # Send mail on failure
            mail_user="f.alich@tu-braunschweig.de",  # Mail to this address
        )
        run_list = RI.get_run_list()
        for key in run_list:
            run_solver_on_inst(key)

        slurminade.join()
        compress_results.distribute()
    else:
        RI.show()

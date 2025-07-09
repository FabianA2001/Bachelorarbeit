import os
from dataclasses import asdict

import slurminade
from dc_triangulation import (
    SAT,
    SAT_TRI,
    Delaunay,
    Graph_Wrapper,
    Gurobi,
    Gurobi_Parameter,
    Gurobi_Tri,
    Gurobi_Tri_Parameter,
    Iterative,
    Ortools,
    Ortools_Parameter,
    Random_Adder,
    Raw_Flips,
    Run_Algbench,
    SAT_Parameter,
    SAT_Tri_Parameter,
)


def get_solvers():
    return [
        Raw_Flips,
        Delaunay,
        Iterative,
        Ortools,
        SAT,
        Random_Adder,
        SAT_TRI,
        Gurobi_Tri,
        Gurobi,
    ]


def get_parameters():
    return [
        SAT_Parameter,
        Ortools_Parameter,
        SAT_Tri_Parameter,
        Gurobi_Tri_Parameter,
        Gurobi_Parameter,
    ]


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
                SAT_Parameter(intersection=True, degree_exact=True, fix_edges=True)
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
                Ortools_Parameter(intersection=True, degree=True, fix_edges=True)
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

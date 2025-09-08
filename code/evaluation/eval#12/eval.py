import os
import random
from dataclasses import asdict

import slurminade
from dc_triangulation import (
    Graph_Wrapper,
    Ortools,
    Ortools_Parameter,
    Run_Algbench,
    load_nodes_from_json,
)

# Font-Konstanten aus show_eval
TITEL_FONT_SIZE = 35
LABEL_FONT_SIZE = 26
ACHSEN_FONT_SIZE = 20
LEGENDE_FONT_SIZE = 30

TIMEOUT = 1800  # 30 minutes in seconds
# path = os.path.join(os.path.dirname(__file__), "instances")
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
                    degree=True,
                    fix_hull=True,
                    all_edges=True,
                    fix_edges=True,
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
    name="Eval15",
)


@slurminade.slurmify()
def run_solver_on_inst(key: str):
    RI.add_entrys(key)


@slurminade.slurmify(mail_type="ALL")
def compress_results():
    # Compress the results to save significant disk space
    RI.compress()


def show():
    table = RI.get_table()
    table = RI.apply_instance(table)
    table = RI.apply_args(table)
    table = table.iloc[0]

    assert table["run_seed"] != 0, "run_seed fehlt in der Lösung."
    seed = table["run_seed"]
    nodes = load_nodes_from_json(
        os.path.join(path, table["instance"], f"{table['file']}.json")
    )
    random.seed(seed)
    random.shuffle(nodes)
    graph = Graph_Wrapper(nodes)
    for edge in table["triangulation"]:
        graph.add_edge(edge[0], edge[1])
    graph.show_and_save(save=".", draw_name=False)


if __name__ == "__main__":
    if False:
        slurminade.update_default_configuration(
            # Your supervisor will tell you these details
            partition="alg",  # Which partition to use. Usually group name.
            constraint="alggen05",  # Which workstations within the partition to use
            exclusive=True,  # To use all cores on a node exclusively
            mail_type="FAIL",  # Send mail on failure
            mail_user="f.alich@tu-braunschweig.de",  # Mail to this address
        )
        run_list = RI.get_run_list()
        with slurminade.JobBundling(max_size=1):
            for key in run_list:
                run_solver_on_inst.distribute(key)

        slurminade.join()
        compress_results.distribute()
    else:
        show()

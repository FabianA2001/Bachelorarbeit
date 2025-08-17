import os
from dataclasses import asdict

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
if __name__ == "__main__":
    table = RI.get_table()
    table = RI.apply_instance(table)
    table = RI.apply_args(table)
    for idx, row in table.iterrows():
        print(f"{row['instance_file']} : {row['solution']['counter']}")

import os
from dataclasses import asdict

from dc_triangulation import (
    Ortools,
    Ortools_Parameter,
    Run_Algbench,
)

TIMEOUT = 50
path = os.path.join(os.path.dirname(__file__), "instances")
figure_path = os.path.join(os.path.dirname(__file__), "figures")
HOST = ["algry01", "algry02", "algry03", "algry04"]


def gesamt():
    outer_parameter = {
        Ortools: [
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    Ortools_Parameter(
                        intersection=True,
                        fix_hull=True,
                        all_edges=True,
                        degree_direction=True,
                        save_state_after_solution=True,
                    )
                ),
            }
        ],
    }

    ri = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        ignore_correct=True,
        # host=HOST,
        name="gesamt",
    )
    table = ri.get_table()
    table = ri.applay_instanze(table)
    table = ri.apply_args(table)
    print(table)


if __name__ == "__main__":
    gesamt()

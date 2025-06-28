import os
from dataclasses import asdict

from dc_triangulation import SAT, Run_Algbench, SAT_Parameter

if __name__ == "__main__":
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
        ],
    }

    ri = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        # figure_path=os.path.dirname(__file__),
    )
    ri.run()
    ri.show()

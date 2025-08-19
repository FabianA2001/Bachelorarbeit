import os
from dataclasses import asdict

from dc_triangulation import (
    Ortools,
    Ortools_Parameter,
    Run_Algbench,
)

asdict
TIMEOUT = 300
path = os.path.join(os.path.dirname(__file__), "instances")
benchmark_path = os.path.join(os.path.dirname(__file__), "lokal_benchmark")
NUMBER_RUNS = 5  # Number of runs for each instance
# This is the entry point for the evaluation script
# It will run the Run_Instance class from run_algbench module


def ja():
    outer_parameter = {
        Ortools: [
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    Ortools_Parameter(
                        intersection=True,
                        degree=True,
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    Ortools_Parameter(
                        intersection=True, degree=True, maximize_edges=0.1
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    Ortools_Parameter(
                        intersection=True, degree=True, maximize_edges=0.5
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    Ortools_Parameter(
                        intersection=True, degree=True, maximize_edges=0.8
                    )
                ),
            },
        ]
    }

    RI = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        path_benchmark=benchmark_path,
        figure_path=os.path.dirname(__file__),
        # host=["algra01", "algra02", "algra03", "algra04", "algra05", "algra06"],
        name="ja",
    )

    RI.show(timelimit=100)


def nein():
    outer_parameter = {
        Ortools: [
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    Ortools_Parameter(
                        intersection=True,
                        degree=True,
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    Ortools_Parameter(
                        intersection=True, degree=True, maximize_edges=-0.1
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    Ortools_Parameter(
                        intersection=True, degree=True, maximize_edges=-0.5
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    Ortools_Parameter(
                        intersection=True, degree=True, maximize_edges=-0.8
                    )
                ),
            },
        ]
    }

    RI = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        path_benchmark=benchmark_path,
        figure_path=os.path.dirname(__file__),
        ignore_correct=True,
        # host=["algra01", "algra02", "algra03", "algra04", "algra05", "algra06"],
        name="nein",
    )
    RI.show()


if __name__ == "__main__":
    ja()
    nein()

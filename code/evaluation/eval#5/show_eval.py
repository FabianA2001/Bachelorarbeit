import os
from dataclasses import asdict

from dc_triangulation import (
    SAT,
    Run_Algbench,
    SAT_Parameter,
)

TIMEOUT = 300
path = os.path.join(os.path.dirname(__file__), "instances")
figure_path = os.path.join(os.path.dirname(__file__), "figures")
lokal_benchmark_path = os.path.join(os.path.dirname(__file__), "lokal_benchmark")
HOST = ["algry01", "algry02", "algry03", "algry04"]


def show_exact():
    outer_parameter = {
        SAT: [
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True, degree_exact=True, degree_encoding=1
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True, degree_exact=True, degree_encoding=2
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True, degree_exact=True, degree_encoding=3
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True, degree_exact=True, degree_encoding=6
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True, degree_exact=True, degree_encoding=7
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True, degree_exact=True, degree_encoding=8
                    )
                ),
            },
        ]
    }
    arg_names = {
        "SAT": [
            "sequential counters",
            "sorting networks",
            "cardinality networks",
            "totalizer",
            "modulo totalizer ",
            "modulo totalizer for k-cardinality",
        ]
    }
    ri = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        path_benchmark=lokal_benchmark_path,
        host=HOST,
        name="exact",
        arg_names=arg_names,
        show_solver_in_legend=False,
    )
    ri.show(block=False)


def show_atleast():
    outer_parameter = {
        SAT: [
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True, degree_atleast=True, degree_encoding=1
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True, degree_atleast=True, degree_encoding=2
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True, degree_atleast=True, degree_encoding=3
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True, degree_atleast=True, degree_encoding=6
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True, degree_atleast=True, degree_encoding=7
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True, degree_atleast=True, degree_encoding=8
                    )
                ),
            },
        ]
    }
    arg_names = {
        "SAT": [
            "sequential counters",
            "sorting networks",
            "cardinality networks",
            "totalizer",
            "modulo totalizer ",
            "modulo totalizer for k-cardinality",
        ]
    }

    ri = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        path_benchmark=lokal_benchmark_path,
        host=HOST,
        name="atleast",
        arg_names=arg_names,
        show_solver_in_legend=False,
    )
    ri.show(block=False)


def show_subset():
    outer_parameter = {
        SAT: [
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True, degree_subset=True, degree_encoding=1
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True, degree_subset=True, degree_encoding=2
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True, degree_subset=True, degree_encoding=3
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True, degree_subset=True, degree_encoding=6
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True, degree_subset=True, degree_encoding=7
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True, degree_subset=True, degree_encoding=8
                    )
                ),
            },
        ]
    }
    arg_names = {
        "SAT": [
            "sequential counters",
            "sorting networks",
            "cardinality networks",
            "totalizer",
            "modulo totalizer ",
            "modulo totalizer for k-cardinality",
        ]
    }

    ri = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        path_benchmark=lokal_benchmark_path,
        host=HOST,
        name="subset",
        arg_names=arg_names,
        show_solver_in_legend=False,
    )
    ri.show(block=False)


def show_gesamt():
    outer_parameter = {
        SAT: [
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True, degree_subset=True, degree_encoding=1
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True, degree_exact=True, degree_encoding=1
                    )
                ),
            },
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    SAT_Parameter(
                        intersection=True, degree_atleast=True, degree_encoding=1
                    )
                ),
            },
        ]
    }
    arg_names = {
        "SAT": [
            "exakt",
            "mindest",
            "subset",
        ]
    }
    ri = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        path_benchmark=lokal_benchmark_path,
        host=HOST,
        name="gesamt",
        arg_names=arg_names,
        show_solver_in_legend=False,
    )
    ri.show(block=False)


if __name__ == "__main__":
    show_exact()
    show_atleast()
    # show_subset()
    show_gesamt()

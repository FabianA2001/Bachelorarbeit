import os
from dataclasses import asdict

from dc_triangulation import (
    SAT,
    Run_Algbench,
    SAT_Parameter,
)

TIMEOUT = 300
path = os.path.join(os.path.dirname(__file__), "instances_backup")
figure_path = os.path.join(os.path.dirname(__file__), "figures")
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

    ri = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        host=HOST,
        name="exact",
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

    ri = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        host=HOST,
        name="atleast",
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

    ri = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        host=HOST,
        name="subset",
    )
    ri.show(block=False)


if __name__ == "__main__":
    show_exact()
    show_atleast()
    show_subset()

import os
from dataclasses import asdict

from dc_triangulation import (
    SAT,
    Gurobi,
    Gurobi_Parameter,
    Ortools,
    Ortools_Parameter,
    Run_Algbench,
    SAT_Parameter,
)

TIMEOUT = 300
path = os.path.join(os.path.dirname(__file__), "instances")
figure_path = os.path.join(os.path.dirname(__file__), "figures")


def show_lokal(RI: Run_Algbench):
    table = RI.get_table()
    table = RI.apply_instance(table)
    table["total_runtime"] = table["pre_time"] + table["runtime"]

    # Group table by "solver" and "instance_file" and add index to solver names
    # For each solver group with 5 rows, add solver_args column with solver+index (0,1,2,3,4)
    grouped = table.groupby(["solver", "instance_file"])

    # Initialize the new column
    table["solver_args"] = ""

    for (solver, instance_file), group in grouped:
        assert len(group) == 5, (
            f"Expected 5 rows for {solver} on {instance_file}, got {len(group)}"
        )
        # Add index to solver name for groups with exactly 5 rows
        for idx, (original_idx, row) in enumerate(group.iterrows()):
            table.at[original_idx, "solver_args"] = f"{solver}_{idx}"

    RI.create_cactus(
        table=table,
        y="total_runtime",
        block=False,
        timelimit=TIMEOUT,
    )


def show_sat():
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
        ],
    }
    RI = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        host=["algry01", "algry02", "algry03", "algry04"],
        name="SAT",
    )
    show_lokal(RI)


def show_ortools():
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
                    )
                ),
            },
        ],
    }
    RI = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        host=["algry01", "algry02", "algry03", "algry04"],
        name="Ortools",
    )
    show_lokal(RI)


def show_gurobi():
    outer_parameter = {
        Gurobi: [
            {
                "timeout": TIMEOUT,
                "args": asdict(
                    Gurobi_Parameter(
                        intersection=True,
                        degree=True,
                        fix_hull=True,
                        all_edges=True,
                    )
                ),
            },
        ],
    }
    RI = Run_Algbench(
        inst_path=path,
        outer_parameter=outer_parameter,
        figure_path=figure_path,
        host=["algry01", "algry02", "algry03", "algry04"],
        name="gurobi",
    )
    show_lokal(RI)


if __name__ == "__main__":
    show_sat()
    show_ortools()
    show_gurobi()

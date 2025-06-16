from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
import logging
from graph_utils import generate
from solver.delaunay import Delaunay
from graph_utils.node import Node, load_nodes_from_json
from solver.ortools import Ortools
from solver.ortools import Parameter as Ortools_Parameter
from solver.raw_flips import Raw_Flips
from solver.iterative import Iterative
from solver.random_adder import Random_Adder
from solver.sat import SAT
from solver.sat import Parameter as SAT_Parameter
from solver.sat_tri import SAT_TRI
from solver.sat_tri import Parameter as SAT_TRI_Parameter
from graph_utils import run_instance
from utils import setup_logging
import matplotlib.pyplot as plt
import matplotlib._pylab_helpers
from dataclasses import asdict


BENCHMARK_PATH = "./results/benchmark"


def get_solvers():
    return [Raw_Flips, Delaunay, Iterative, Ortools, SAT, Random_Adder, SAT_TRI]


def get_parameters():
    return [SAT_Parameter, Ortools_Parameter, SAT_TRI_Parameter]


def custom_points() -> list[Node]:
    nodes = [
        Node((0, 0), 3),
        Node((1, 1), 3),
        Node((1, 0), 2),
        Node((0, 1), 2),
    ]
    nodes = [
        Node((2, 2)),
        Node((6, 3)),
        Node((5, 4)),
        Node((4, 5)),
        Node((3, 6)),
        Node((1, 8)),
        Node((14, 8)),
        Node((7, 1)),
    ]
    graph = Graph_Wrapper(nodes)
    if True:
        solver = Random_Adder(graph)
        solver.solve(
            {
                "timeout": -1,
                "version": 0.1,
            }
        )
        return graph.get_aktive_graph_nodes()
    else:
        return nodes


def ortools_algorithm(graph):
    solver = Ortools(graph)
    para = Ortools_Parameter(
        intersection=True,
        degree=True,
        number_edges=True,
    )
    logging.info(
        f"solution found: {solver.solve({'timeout': -1, 'args': asdict(para)})}"
    )


def sat_algorithm(graph):
    solver = SAT(graph)
    para = SAT_Parameter(
        add_allEdges_or_exclude_edges=False,
        intersection=True,
        degree_atleast=True,
        fix_hull=True,
        # exclude_edges=True,
    )
    logging.info(
        f"solution found: {solver.solve({'timeout': -1, 'args': asdict(para)})}"
    )


def sat_Tri_algorithm(graph):
    solver = SAT_TRI(graph)
    para = SAT_TRI_Parameter(
        add_allEdges_or_exlucde_edges=True,
        intersection=True,
        degree=True,
    )
    logging.info(
        f"solution found: {solver.solve({'timeout': -1, 'args': asdict(para)})}"
    )


def test_algo():
    PATH = "simple_80/000_random.json"
    # PATH = "iterative_60_10/000_random.json"
    logging.info(f"Loading nodes from {PATH}")
    nodes = load_nodes_from_json(PATH)
    # nodes = custom_points()
    graph = Graph_Wrapper(nodes)
    sat_algorithm(graph)
    # sat_Tri_algorithm(graph)
    # ortools_algorithm(graph)
    graph.show_and_save()


def create_instance():
    NAME = "simple_100"
    FILE_NAME = "random"
    NUMBER_INSTANCE = 5
    NUMBER_NODES = 100
    # STEP = 10
    generate.Generate_Instance(
        NAME,
        FILE_NAME,
        NUMBER_NODES,
        NUMBER_INSTANCE,
        generate.Generate_Nodes_Random(),
        generate.Generate_Edges_Random(),
        width=10000,
        height=10000,
    ).generate()


def run_instance_lokal():
    outer_parameter = {
        SAT: [
            {
                "timeout": -1,
                "args": asdict(
                    SAT_Parameter(
                        add_allEdges_or_exclude_edges=True,
                        intersection=True,
                        degree_atleast=True,
                        fix_hull=True,
                    )
                ),
            }
        ]
    }
    ri = run_instance.Run_Instance(path_benchmark=BENCHMARK_PATH, solver=get_solvers())
    # ri.select(outer_parameter)
    # ri.show_triangulation_from_instance(
    #     algorithm_name="Random",
    #     instance_name="simple_30",
    #     instance_file_name="001_delaunay"
    # )
    ri.run_default(outer_parameter)


def block_plt():
    while matplotlib._pylab_helpers.Gcf.get_all_fig_managers():
        plt.pause(0.1)  # Kleine Pause, um GUI nicht zu blockieren


def main():
    # test_algo()
    # create_instance()
    run_instance_lokal()


if __name__ == "__main__":
    setup_logging()
    logging.info("Start main function.")
    main()
    logging.info("End main function.")
    block_plt()

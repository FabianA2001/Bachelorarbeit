from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from graph_utils.node import move_degree
import logging
from graph_utils import generate
from solver.delaunay import Delaunay
from graph_utils.node import Node, load_nodes_from_json
from solver.ortools import Ortools
from solver.raw_flips import Raw_Flips
from solver.iterative import Iterative
from solver.random_adder import Random_Adder
from solver.sat import SAT
from graph_utils import run_instance
from utils import setup_logging
import matplotlib.pyplot as plt
import matplotlib._pylab_helpers


BENCHMARK_PATH = "./results/benchmark"


def get_solvers():
    return [
        Raw_Flips,
        Delaunay,
        Iterative,
        Ortools,
        SAT,
        Random_Adder,
    ]


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


def test_algo():
    # nodes = load_nodes_from_json("iterative_60_10/004_random.json")
    nodes = load_nodes_from_json("simple_80/000_random.json")
    # nodes = load_nodes_from_json("simple_10/000_delaunay_flips.json")
    # nodes = load_nodes_from_json("test_algo.json")
    # nodes = custom_points()
    graph = Graph_Wrapper(nodes)
    graph.name = "Test Algo"
    # time_function(graph.add_all_possible_edges)(default_for_active=True)
    # time_function(graph.get_all_intersections)()
    # print(*graph.get_all_edges(), sep="\n")
    solver = SAT(graph)
    solver.solve(
        {
            "timeout": -1,
            "version": 0.6,
        }
    )
    graph.show_and_save()


def move():
    nodes = generate.gen_nodes(30, 4000, 4000)
    graph = Graph_Wrapper(nodes)
    solver = Delaunay(graph)
    solver.solve(
        {
            "timeout": 10,
            "version": 0.1,
        }
    )

    graph.show_and_save(show=False)
    graph.name = "Delaunay"
    nodes2 = graph.get_aktive_graph_nodes()
    for _ in range(40):
        nodes2 = move_degree(nodes2, 1, 1, 2)
        graph2 = Graph_Wrapper(nodes2)
        solver2 = Ortools(graph2)
        if solver2.solve(
            {
                "timeout": 10,
                "version": 0.1,
            }
        ):
            break
    else:
        print("No solution found after 100 iterations")
        graph2.show_and_save()
        return
    graph2.save_graph_as_json("moved_delaune.json")
    graph2.show_and_save()


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
    ri = run_instance.Run_Instance(path_benchmark=BENCHMARK_PATH, solver=get_solvers())
    ri.select()
    # ri.show_triangulation_from_instance(
    #     algorithm_name="Random",
    #     instance_name="simple_30",
    #     instance_file_name="001_delaunay"
    # )
    # ri.run_default()


def block_plt():
    while matplotlib._pylab_helpers.Gcf.get_all_fig_managers():
        plt.pause(0.1)  # Kleine Pause, um GUI nicht zu blockieren


def main():
    test_algo()
    # create_instance()
    # run_instance_lokal()


if __name__ == "__main__":
    setup_logging()
    logging.info("Start main function.")
    main()
    logging.info("End main function.")
    block_plt()

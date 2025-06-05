from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from graph_utils.node import move_degree, load_nodes_from_json
import logging
from graph_utils import generate
from solver.delaunay import Delaunay
from graph_utils.node import Node
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
        Node("A", (0, 0), 3),
        Node("B", (0, 1), 2),
        Node("C", (1, 0), 2),
        Node("D", (1, 1), 3),
    ]
    return nodes


def test_algo():
    nodes = load_nodes_from_json("simple_40/000_delaunay_flips.json")
    # for solver in [Raw_Flips, Random_Adder, Cycle_Add, Delaunay, Iterative]:
    graph = Graph_Wrapper(nodes)
    solver = SAT(graph)
    solver.solve(timeout=7)
    # logging.info(f"evaluation: {graph.evaluate_graph()}")
    graph.show_and_save()


def move():
    nodes = generate.gen_nodes(30, 4000, 4000)
    graph = Graph_Wrapper(nodes)
    solver = Delaunay(graph)
    solver.solve()

    graph.show_and_save(show=False)
    graph.name = "Delaunay"
    nodes2 = graph.get_aktive_graph_nodes()
    for _ in range(40):
        nodes2 = move_degree(nodes2, 1, 1, 2)
        graph2 = Graph_Wrapper(nodes2)
        solver2 = Ortools(graph2)
        if solver2.solve():
            break
    else:
        print("No solution found after 100 iterations")
        graph2.show_and_save()
        return
    graph2.save_graph_as_json("moved_delaune.json")
    graph2.show_and_save()


def create_instance():
    NAME = "N_Gon_60"
    FILE_NAME = "random"
    NUMBER_INSTANCE = 11
    NUMBER_NODES = 60
    STEP = 5
    generate.Generate_Instance(
        NAME,
        FILE_NAME,
        NUMBER_NODES,
        NUMBER_INSTANCE,
        generate.Generate_Nodes_Iterativ_N_Gon(STEP, NUMBER_INSTANCE, 300),
        generate.Generate_Edges_Random(),
        width=1000,
        height=1000,
    ).generate()


def run_instance_lokal():
    ri = run_instance.Run_Instance(path_benchmark=BENCHMARK_PATH, solver=get_solvers())
    ri.select()
    # ri.show_triangulation_from_instance(
    #     algorithm_name="SAT",
    #     instance_name="simple_20",
    #     instance_file_name="000_delaunay_flips"
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

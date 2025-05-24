from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from graph_utils.node import move_degree
import logging
from graph_utils import generate
from solver.delaunay import Delaunay
from graph_utils.node import Node
from solver.ortools import Ortools
from solver.raw_flips import Raw_Flips
from solver.iterative import Iterative
from solver.cycle_add import Cycle_Add
from graph_utils import run_instance
from utils import setup_logging
from graph_utils.node import load_nodes_from_json
import matplotlib.pyplot as plt
import matplotlib._pylab_helpers


def solver():
    Raw_Flips
    Delaunay
    Iterative
    Ortools
    Cycle_Add


def custom_points() -> list[Node]:
    nodes = [
        Node("A", (0, 0)),
        Node("B", (0, 1)),
        Node("C", (1, 0)),
        Node("D", (1, 1)),
    ]
    return nodes


def test_algo():
    nodes = load_nodes_from_json("simple_20/000_delaunay_flips.json")
    graph = Graph_Wrapper(nodes)
    solver = Cycle_Add(graph)
    solver.solve(timeout=-1)
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


def run_instance_lokal():
    inst = "simple_20"
    run_instance.run_solver_on_instance(solver_type=Cycle_Add, instance_name=inst)
    run_instance.show_results(inst)
    run_instance.show_percentage_of_correct_nodes(inst)


def create_instance():
    generate.Generate_Delaunay(
        name="simple_20",
        number_nodes=20,
        number_instances=2,
        # number_flips=100,
    ).generate()


def test(a):
    print(a)
    logging.error("Error in test function")
    return a


def main():
    # test_algo()
    # create_instance()
    run_instance_lokal()


if __name__ == "__main__":
    setup_logging()
    logging.info("Start main function.")
    main()
    logging.info("End main function.")
    while matplotlib._pylab_helpers.Gcf.get_all_fig_managers():
        plt.pause(0.1)  # Kleine Pause, um GUI nicht zu blockieren

from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from graph_utils.node import move_degree
import logging
from graph_utils import generate
from solver.delaunay import Delaunay
from graph_utils.node import Node
from solver.ortools import Ortools
from graph_utils import run_instance
from utils import setup_logging


def custom_points() -> list[Node]:
    nodes = [
        Node("A", (0, 0)),
        Node("B", (0, 1)),
        Node("C", (1, 0)),
        Node("D", (1, 1)),
    ]
    return nodes


def test_algo():
    nodes = generate.gen_nodes(50, 500, 500)
    graph = Graph_Wrapper(nodes)
    solver = Ortools(graph)
    print(solver.solve(timeout=5))
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
    run_instance.run_solver_on_instance(
        solver=Ortools(),
        instance_name=inst,
    )
    run_instance.show_results(inst)


def create_instance():
    generate.Generate_Delaunay_Flips(
        name="simple_40",
        number_nodes=40,
        number_instances=10,
        number_flips=50,
    ).generate()


def test(a):
    print(a)
    logging.error("Error in test function")
    return a


def main():
    setup_logging()
    logging.info("Start main function.")
    test_algo()
    logging.info("End main function.")


if __name__ == "__main__":
    main()
    # test für commit

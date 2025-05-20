from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from graph_utils.node import (
    load_nodes_from_json,
)
import logging
from graph_utils import generate
from solver.delaunay import Delaunay
from graph_utils.node import Node
from solver.ortools import Ortools
from graph_utils import run_instance
from utils import setup_logging, time_function


def custom_points() -> list[Node]:
    nodes = [
        Node("A", (0, 0)),
        Node("B", (0, 1)),
        Node("C", (1, 0)),
        Node("D", (1, 1)),
    ]
    return nodes


def test_algo():
    # nodes = generate.gen_nodes(10, 500, 500)
    # nodes = custom_points()
    nodes = load_nodes_from_json("test.json")
    # save_nodes_as_json(nodes, "test.json")
    graph = Graph_Wrapper(nodes)
    solver = Delaunay(graph)
    solver.solve()
    graph.add_edge("66", "97", True)
    # graph.show_and_save()
    print(time_function(graph.check_if_triangulation_with_degree_constraint)())


def move():
    nodes = generate.gen_nodes(20, 100, 100)
    graph = Graph_Wrapper(nodes)
    solver = Delaunay(graph)
    solver.solve()

    graph.show_and_save(show=False)
    graph.name = "Delaunay"
    nodes2 = graph.get_aktive_graph_nodes()
    graph2 = Graph_Wrapper(nodes2)
    graph2.move_node()
    solver2 = Ortools(graph2)
    solver2.solve()
    graph2.show_and_save(show=False)


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
    return a


def main():
    setup_logging()
    logging.info("Start main function.")
    test_algo()
    logging.info("End main function.")


if __name__ == "__main__":
    main()
    # test für commit

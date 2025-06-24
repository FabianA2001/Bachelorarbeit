import logging
import os
from dataclasses import asdict

from dc_triangulation import (
    SAT,
    SAT_TRI,
    Delaunay,
    Graph_Wrapper,
    Iterative,
    Node,
    Ortools,
    Ortools_Parameter,
    Random_Adder,
    Raw_Flips,
    SAT_Parameter,
    SAT_TRI_Parameter,
    generate,
    load_nodes_from_json,
    time_function,
)


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
        degree_direction=True,
    )
    logging.info(
        f"solution found: {solver.solve({'timeout': 30, 'args': asdict(para)})}"
    )


def sat_algorithm(graph):
    solver = SAT(graph)
    para = SAT_Parameter(
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


def run_algo():
    PATH = os.path.join(
        os.path.dirname(__file__), "instance", "simple_80", "000_random.json"
    )
    logging.info(f"Loading nodes from {PATH}")
    nodes = load_nodes_from_json(PATH)
    # nodes = custom_points()
    graph = Graph_Wrapper(nodes)
    cpp = time_function(graph.get_all_intersections_cpp)()
    py = time_function(graph.get_all_intersections)()
    assert cpp == py, (
        "Intersection results differ between C++ and Python implementations"
    )

    # sat_algorithm(graph)
    # sat_Tri_algorithm(graph)
    # ortools_algorithm(graph)
    # graph.add_edge(0, 5)
    # graph.show_and_save(show=False, save=".")


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


if __name__ == "__main__":
    run_algo()
    # create_instance()

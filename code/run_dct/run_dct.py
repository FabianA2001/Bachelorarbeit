import logging
import os
from dataclasses import asdict

from dc_triangulation import (
    SAT,
    SAT_TRI,
    Delaunay,
    Graph_Wrapper,
    Gurobi,
    Gurobi_Parameter,
    Gurobi_Tri,
    Gurobi_Tri_Parameter,
    Iterative,
    Node,
    Ortools,
    Ortools_Parameter,
    Random_Adder,
    Raw_Flips,
    SAT_Parameter,
    SAT_Tri_Parameter,
    generate,
    load_nodes_from_json,
    time_function,
)


def get_solvers():
    return [
        Raw_Flips,
        Delaunay,
        Iterative,
        Ortools,
        SAT,
        Random_Adder,
        SAT_TRI,
        Gurobi_Tri,
        Gurobi,
    ]


def get_parameters():
    return [
        SAT_Parameter,
        Ortools_Parameter,
        SAT_Tri_Parameter,
        Gurobi_Tri_Parameter,
        Gurobi_Parameter,
    ]


time_function


def custom_points() -> list[Node]:
    if False:
        return [
            Node((0, 0), 3),
            Node((1, 1), 3),
            Node((1, 0), 2),
            Node((0, 1), 2),
        ]
    else:
        nodes = [
            Node((5, 10)),
            Node((2, 6)),
            Node((6, 5)),
            Node((9, 3)),
            Node((0, 10)),
            Node((9, 5)),
            Node((1, 2)),
            # Node((8, 6)),
            # Node((2, 3)),
            # Node((2, 10)),
        ]
        graph = Graph_Wrapper(nodes)
        solver = Random_Adder(graph)
        solver.solve({"timeout": -1, "ignore_degree": True})
        return graph.get_aktive_graph_nodes()


def ortools_algorithm(graph):
    solver = Ortools(graph)
    para = Ortools_Parameter(
        intersection=True,
        degree=True,
        fix_hull=True,
        # all_edges=True,
        # exclude_edges=True,
    )
    logging.info(
        f"solution found: {solver.solve({'timeout': 300, 'args': asdict(para)})}"
    )


def sat_algorithm(graph):
    solver = SAT(graph)
    para = SAT_Parameter(
        intersection=True,
        degree_atleast=True,
        fix_hull=True,
        all_edges=True,
        # exclude_edges=True,
    )
    logging.info(
        f"solution found: {solver.solve({'timeout': -1, 'args': asdict(para)})}"
    )


def sat_Tri_algorithm(graph):
    solver = SAT_TRI(graph)
    para = SAT_Tri_Parameter(intersection=True, degree=True, exclude_edges=True)
    logging.info(
        f"solution found: {solver.solve({'timeout': -1, 'args': asdict(para)})}"
    )


def gurobi_tri_algorithm(graph):
    solver = Gurobi_Tri(graph)
    para = Gurobi_Tri_Parameter(intersection=True, degree=True, exclude_edges=True)
    logging.info(
        f"solution found: {solver.solve({'timeout': 60, 'args': asdict(para)})}"
    )


def gurobi_algorithm(graph):
    solver = Gurobi(graph)
    para = Gurobi_Parameter(
        fix_hull=True,
        degree=True,
        intersection=True,
        # exclude_edges=True,
        # all_edges=True,
    )
    logging.info(
        f"solution found: {solver.solve({'timeout': 300, 'args': asdict(para)})}"
    )


def run_algo():
    # PATH = os.path.join(
    #     os.path.dirname(__file__), "instance", "simple_30", "000_delaunay.json"
    # )
    # PATH = os.path.join(
    #     os.path.dirname(__file__), "instance", "simple_80", "000_random.json"
    # )
    # PATH = os.path.join(
    #     os.path.dirname(__file__), "instance", "simple_60", "000_delaunay_flips.json"
    # )
    PATH = os.path.join(
        os.path.dirname(__file__),
        "instance",
        "random_impossible",
        "000_random_impossible_30.json",
    )
    logging.info(f"Loading nodes from {PATH}")
    nodes = load_nodes_from_json(PATH)
    # nodes = custom_points()
    graph = Graph_Wrapper(nodes)
    print(len(time_function(graph.get_intersection_clique)()))
    # sat_algorithm(graph)
    # sat_Tri_algorithm(graph)
    # ortools_algorithm(graph)
    # gurobi_tri_algorithm(graph)
    # gurobi_algorithm(graph)

    # graph.add_edge(0, 5)
    # graph.add_all_possible_edges(True)
    # graph.show_and_save()


def create_instance():
    NAME = "delaunay_impossible"
    FILE_NAME = "delaunay_impossible"
    NUMBER_INSTANCE = 6
    NUMBER_NODES = 80
    STEP = 10
    FLIPS = 300
    generate.Generate_Instance(
        NAME,
        FILE_NAME,
        NUMBER_NODES,
        NUMBER_INSTANCE,
        generate.Generate_Nodes_Iterativ(STEP, NUMBER_INSTANCE),
        generate.Generate_Edges_Delaunay(),
        generate.Generate_Impossible_Move_Degree(),
        path="instance",
        width=10000,
        height=10000,
    ).generate()


if __name__ == "__main__":
    run_algo()
    # create_instance()

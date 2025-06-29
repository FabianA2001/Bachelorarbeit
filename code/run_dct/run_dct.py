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
)


def get_solvers():
    return [Raw_Flips, Delaunay, Iterative, Ortools, SAT, Random_Adder, SAT_TRI, Gurobi]


def get_parameters():
    return [SAT_Parameter, Ortools_Parameter, SAT_TRI_Parameter, Gurobi_Parameter]


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
        all_edges=True,
        exclude_edges=True,
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
        all_edges=True,
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


def gurobi_algorithm(graph):
    solver = Gurobi(graph)
    para = Gurobi_Parameter(
        intersection=True,
        degree=True,
    )
    logging.info(
        f"solution found: {solver.solve({'timeout': -1, 'args': asdict(para)})}"
    )


def run_algo():
    PATH = os.path.join(
        os.path.dirname(__file__), "instance", "simple_10", "000_delaunay_flips.json"
    )
    logging.info(f"Loading nodes from {PATH}")
    nodes = load_nodes_from_json(PATH)
    # nodes = custom_points()
    graph = Graph_Wrapper(nodes)
    # x1 = graph.get_all_intersections_cpp()
    # x2 = graph.get_all_intersections()
    # assert x1 == x2
    # print(*x1.items(), sep="\n")
    # sat_algorithm(graph)
    # sat_Tri_algorithm(graph)
    ortools_algorithm(graph)
    # gurobi_algorithm(graph)

    # graph.add_edge(0, 5)
    # graph.add_all_possible_edges(True)
    graph.show_and_save()


def create_instance():
    NAME = "random_impossible"
    FILE_NAME = "random_impossible"
    NUMBER_INSTANCE = 6
    NUMBER_NODES = 80
    STEP = 10
    generate.Generate_Instance(
        NAME,
        FILE_NAME,
        NUMBER_NODES,
        NUMBER_INSTANCE,
        generate.Generate_Nodes_Iterativ(STEP, NUMBER_INSTANCE),
        generate.Generate_Edges_Random_Impossible(),
        path="instance",
        width=10000,
        height=10000,
    ).generate()


if __name__ == "__main__":
    run_algo()
    # create_instance()

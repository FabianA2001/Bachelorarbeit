import logging
import os
from dataclasses import asdict

from dc_triangulation import (
    SAT,
    SAT_TRI,
    Cadical,
    Cadical_Parameter,
    Count,
    Delaunay,
    Graph_Wrapper,
    Greedy,
    Gurobi,
    Gurobi_Parameter,
    Gurobi_Tri,
    Gurobi_Tri_Parameter,
    Iterative,
    Node,
    Ortools,
    Ortools_Parameter,
    OrTools_Tri,
    Ortools_Tri_Parameter,
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
        Greedy,
        Raw_Flips,
        Delaunay,
        Iterative,
        Ortools,
        SAT,
        Random_Adder,
        SAT_TRI,
        Gurobi_Tri,
        Gurobi,
        OrTools_Tri,
        Cadical,
        Count,
    ]


def get_parameters():
    return [
        SAT_Parameter,
        Ortools_Parameter,
        SAT_Tri_Parameter,
        Gurobi_Tri_Parameter,
        Gurobi_Parameter,
        Ortools_Tri_Parameter,
        Cadical_Parameter,
    ]


time_function


def custom_points() -> list[Node]:
    if True:
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


def multiple_solutions() -> list[Node]:
    return [
        Node((0, 0), 4),
        Node((5, 0), 4),
        Node((5, 5), 4),
        Node((0, 5), 4),
        Node((1, 1), 5),
        Node((4, 1), 4),
        Node((4, 4), 5),
        Node((1, 4), 4),
    ]


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


# 1,2,3,6,7,8
def sat_algorithm(graph):
    solver = SAT(graph)
    para = SAT_Parameter(
        intersection=True,
        degree_exact=True,
        # fix_hull=True,
        # all_edges=True,
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


def ortools_tri_algorithm(graph):
    solver = OrTools_Tri(graph)
    para = Ortools_Tri_Parameter(intersection=True, degree=True)
    logging.info(
        f"solution found: {solver.solve({'timeout': 60, 'args': asdict(para)})}"
    )


def count_algorithm(graph):
    solver = Count(graph)
    logging.info(f"solution found: {solver.solve({'timeout': -1})}")


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


def cadical_algorithm(graph, nodes=None):
    solver = Cadical(graph)
    para = Cadical_Parameter(
        degree=True,
        intersection=True,
        fix_hull=True,
    )
    solution = solver.solve({"timeout": -1, "args": asdict(para)})
    logging.info(f"solution found: {solution.get('success', False)}")
    if nodes is None:
        return
    SAVE = "cadical_figures"
    # wenn es den ordner SAVE gibt leere ihn
    if os.path.exists(SAVE):
        import shutil

        shutil.rmtree(SAVE)
    os.makedirs(SAVE, exist_ok=True)

    max_edges = len(solver.edges)
    for i, vars in enumerate(solution.get("debug_vars", [])):
        lokal_graph = Graph_Wrapper(nodes)
        lokal_graph.name = f"{i}"
        for j, var in enumerate(vars):
            if j >= max_edges:
                break
            if var == 1:
                edge = solver.edges[j]
                lokal_graph.add_edge(edge[0], edge[1])
        lokal_graph.show_and_save(show=False, save=SAVE)


def run_algo():
    # PATH = os.path.join(
    #     os.path.dirname(__file__), "instance", "simple_20", "001_delaunay_flips.json"
    # )
    PATH = os.path.join(
        os.path.dirname(__file__), "instance", "simple_80", "000_random.json"
    )
    # PATH = os.path.join(
    #     os.path.dirname(__file__), "instance", "simple_60", "000_delaunay_flips.json"
    # )
    # PATH = os.path.join(
    #     os.path.dirname(__file__),
    #     "instance",
    #     "random_impossible",
    #     "000_random_impossible_30.json",
    # )
    # PATH = os.path.join(
    #     os.path.dirname(__file__),
    #     "instance",
    #     "iterative_80_10",
    #     "003_random_60.json",
    # )
    # PATH = os.path.join(
    #     os.path.dirname(__file__),
    #     "instance",
    #     "N_Gon_60",
    #     "006_random.json",
    # )
    logging.info(f"Loading nodes from {PATH}")
    nodes = load_nodes_from_json(PATH)
    # nodes = custom_points()
    # nodes = multiple_solutions()
    graph = Graph_Wrapper(nodes)
    # solver = Greedy(graph)
    # solver.solve({"timeout": -1})

    # time_function(lambda: graph.get_intersection_clique_cpp)()
    # sat_algorithm(graph)
    # cadical_algorithm(graph, nodes)
    count_algorithm(graph)
    # sat_Tri_algorithm(graph)
    # ortools_algorithm(graph)
    # ortools_tri_algorithm(graph)
    # gurobi_tri_algorithm(graph)
    # gurobi_algorithm(graph)

    # graph.add_all_possible_edges(True)
    # graph.show_and_save()


def create_instance():
    FLIPS = 500
    for NAME, gen in zip(
        ["d_flips", "delaunay", "greedy", "iterative", "random"],
        [
            generate.Generate_Edges_Delaunay_Flips(FLIPS),
            generate.Generate_Edges_Delaunay(),
            generate.Generate_Edges_Greedy(),
            generate.Generate_Edges_Iterative(),
            generate.Generate_Edges_Random(),
        ],
    ):
        INST_NAME = NAME
        for i in [30, 40, 50, 60]:
            FILE_NAME = f"{NAME}"
            generate.Generate_Instance(
                INST_NAME,
                FILE_NAME,
                i,
                2,
                generate.Generate_Nodes_Random(),
                gen,
                path="instance",
                width=10000,
                height=10000,
            ).generate()
            FILE_NAME = f"{NAME}_impossible_move"
            generate.Generate_Instance(
                INST_NAME,
                FILE_NAME,
                i,
                1,
                generate.Generate_Nodes_Random(),
                gen,
                generate.Generate_Impossible_Move_Degree(amount=5, times=10),
                path="instance",
                width=10000,
                height=10000,
            ).generate()
            FILE_NAME = f"{NAME}_impossible_change"
            generate.Generate_Instance(
                INST_NAME,
                FILE_NAME,
                i,
                1,
                generate.Generate_Nodes_Random(),
                gen,
                generate.Generate_Impossible_Change_Degree(times=10),
                path="instance",
                width=10000,
                height=10000,
            ).generate()


if __name__ == "__main__":
    run_algo()
    # create_instance()

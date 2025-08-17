import json
import logging
import os
import random
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
    save_nodes_as_json,
    time_function,
)


def save_solution_as_json(solution, filename):
    """
    Saves a solution dictionary as JSON file.

    Args:
        solution: The solution dictionary to save
        filename: Name of the JSON file (without extension)
        output_dir: Directory to save the file in (default: "solutions")
    """
    if solution is None:
        logging.warning(f"Solution is None, skipping save for {filename}")
        return

    # Ensure filename has .json extension
    if not filename.endswith(".json"):
        filename += ".json"

    try:
        with open(filename, "w") as f:
            json.dump(solution, f, indent=4, default=str)
        logging.info(f"Solution saved to: {filename}")
    except Exception as e:
        logging.error(f"Error saving solution to {filename}: {e}")


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
            Node((4, 1), 3),
            Node((4, 3), 5),
            Node((2, 4), 3),
            Node((6, 4), 3),
            Node((2, 5), 5),
            Node((6, 5), 5),
            Node((4, 7), 6),
            Node((2, 8), 3),
            Node((2, 10), 3),
            Node((6, 10), 3),
            Node((6, 8), 3),
        ]
    else:
        nodes = [
            Node((9, 3)),
            Node((5, 7)),
            Node((13, 7)),
            Node((5, 10)),
            Node((13, 10)),
            Node((5, 13)),
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
        # degree=True,
        fix_hull=True,
        all_edges=True,
        min_max_direction=True,
        # evaluation_direction=True,
        # exclude_edges=True,
        save_state_after_solution=True,
    )
    solution = solver.solve({"timeout": 300, "args": asdict(para)})
    logging.info(f"solution found: {solution}")

    # Save solution as JSON
    save_solution_as_json(solution, "ortools_solution")


# 1,2,3,6,7,8
def sat_algorithm(graph):
    solver = SAT(graph)
    para = SAT_Parameter(
        intersection=True,
        degree_atleast=True,
        fix_hull=True,
        exclude_edges=True,
        all_edges=True,
        # exclude_edges=True,
    )
    logging.info(
        f"solution found: {solver.solve({'timeout': 30, 'args': asdict(para)})}"
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
    solution = solver.solve({"timeout": 900})
    logging.info(f"solution found: {solution}")
    logging.info(
        f"lenght of seen combinations: {len(list(solution['seen_combinations'])[0])}"
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


def raw_flips_algorithm(graph):
    solver = Raw_Flips(graph)
    logging.info(f"solution found: {solver.solve({'timeout': 50})}")


def cadical_algorithm(graph, nodes=None):
    import shutil

    # print(nodes[3])
    # print(nodes[27])
    # return

    solver = Cadical(graph)
    para = Cadical_Parameter(
        degree=True,
        intersection=True,
        fix_hull=True,
        # save_state=True,
        optimize_propagation=True,
        exclude_edges=True,
    )
    SVG_SAVE = "svg_figures"
    if os.path.exists(SVG_SAVE):
        shutil.rmtree(SVG_SAVE)

    solution = solver.solve({"timeout": -1, "args": asdict(para)})
    logging.info(f"solution found: {solution.get('success', False)}")
    if nodes is None:
        return
    SAVE = "cadical_figures"
    # wenn es den ordner SAVE gibt leere ihn

    if os.path.exists(SAVE):
        shutil.rmtree(SAVE)
    os.makedirs(SAVE, exist_ok=True)

    max_edges = len(solver.edges)
    debug_vars = solution.get("debug_vars", [])
    for i, vars in enumerate(debug_vars):
        lokal_graph = Graph_Wrapper(nodes)
        lokal_graph.name = f"{i}"
        for j, var in enumerate(vars):
            if j >= max_edges:
                break
            if var == 1:
                edge = solver.edges[j]
                lokal_graph.add_edge(edge[0], edge[1])
            if var == 0:
                edge = solver.edges[j]
                lokal_graph.add_edge(edge[0], edge[1], active=False)
                lokal_graph.edge_show_false(edge[0], edge[1])
        lokal_graph.show_and_save(show=False, save=SAVE, show_set_false=True)


def show_all_instanzes():
    grpahes = []
    for PATH in [
        os.path.join(
            os.path.dirname(__file__),
            "instance",
            "d_flips",
            "004_d_flips_40.json",
        ),
        os.path.join(
            os.path.dirname(__file__),
            "instance",
            "delaunay",
            "004_delaunay_40.json",
        ),
        os.path.join(
            os.path.dirname(__file__),
            "instance",
            "greedy",
            "004_greedy_40.json",
        ),
        os.path.join(
            os.path.dirname(__file__),
            "instance",
            "iterative",
            "004_iterative_40.json",
        ),
        os.path.join(
            os.path.dirname(__file__),
            "instance",
            "random",
            "004_random_40.json",
        ),
    ]:
        nodes = load_nodes_from_json(PATH)
        grpahes.append(Graph_Wrapper(nodes))
    for name, graph in zip(
        ["d_flips", "delaunay", "greedy", "iterative", "random"], grpahes
    ):
        sat_algorithm(graph)
        graph.name = f"graph_{name}"
        graph.show_and_save(save="figures", block=False)


def run_algo():
    # PATH = os.path.join(
    #     os.path.dirname(__file__), "instance", "simple_30", "000_delaunay.json"
    # )
    PATH = os.path.join(
        os.path.dirname(__file__),
        "eval_instance",
        "d_flips",
        "000_d_flips_30.json",
    )

    logging.info(f"Loading nodes from {PATH}")
    nodes = load_nodes_from_json(PATH)

    # for i, node in enumerate(nodes):
    #     print(i, node.pos)
    # nodes = custom_points()
    # nodes = multiple_solutions()
    graph = Graph_Wrapper(nodes)
    # solver = Greedy(graph)
    # solver.solve({"timeout": -1})

    # time_function(lambda: graph.get_intersection_clique_cpp)()
    # sat_algorithm(graph)
    cadical_algorithm(graph, nodes)
    # count_algorithm(graph)
    # sat_Tri_algorithm(graph)
    # ortools_algorithm(graph)
    # ortools_tri_algorithm(graph)
    # gurobi_tri_algorithm(graph)
    # gurobi_algorithm(graph)
    # raw_flips_algorithm(graph)

    # graph.add_all_possible_edges(True)
    # logging.info(f"evluation: {graph.evaluate()}")
    graph.show_and_save()


def permute_instance():
    CURRENT_PATH = os.path.join(
        os.path.dirname(__file__), "eval_instance", "delaunay_1"
    )
    TARGET_PATH = os.path.join(os.path.dirname(__file__), "eval_instance")
    TARGET_DIR = "delaunay"
    NUMBER_PERMUTATION = 5 - 1
    for i in range(NUMBER_PERMUTATION):
        for filename in os.listdir(CURRENT_PATH):
            nodes = load_nodes_from_json(os.path.join(CURRENT_PATH, filename))
            with open(os.path.join(CURRENT_PATH, filename), "r") as f:
                data = json.load(f)
            possible = data.get("possible", None)
            random.shuffle(nodes)
            lokal_target_path = os.path.join(TARGET_PATH, f"{TARGET_DIR}_{i + 2}")
            save_nodes_as_json(
                nodes,
                lokal_target_path,
                filename=filename,
            )
            if possible is not None:
                path = os.path.join(lokal_target_path, filename)
                with open(path, "r") as f:
                    data = json.load(f)
                data["possible"] = possible
                with open(path, "w") as f:
                    json.dump(data, f, indent=4)


def create_instance():
    FLIPS = 500
    PATH = "instance"
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
        INST_NAME = "example_20"
        for i in [20]:
            FILE_NAME = f"{NAME}"
            generate.Generate_Instance(
                INST_NAME,
                FILE_NAME,
                i,
                2,
                generate.Generate_Nodes_Random(),
                gen,
                path=PATH,
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
                path=PATH,
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
                path=PATH,
                width=10000,
                height=10000,
            ).generate()


def generate_example():
    FLIPS = 500
    PATH = "instance"
    nodes = generate.gen_nodes(20, 10000, 10000)
    for NAME, gen in zip(
        ["Delaunay_Flips", "Delaunay", "Greedy", "Iterative", "Random"],
        [
            generate.Generate_Edges_Delaunay_Flips(FLIPS),
            generate.Generate_Edges_Delaunay(),
            generate.Generate_Edges_Greedy(),
            generate.Generate_Edges_Iterative(),
            generate.Generate_Edges_Random(),
        ],
    ):
        INST_NAME = "example_20"
        FILE_NAME = f"{NAME}"
        generate.Generate_Instance(
            INST_NAME,
            FILE_NAME,
            20,
            1,
            generate.Generate_Nodes_Given(nodes),
            gen,
            path=PATH,
            width=10000,
            height=10000,
        ).generate()


def draw_example():
    path = os.path.join(
        os.path.dirname(__file__),
        "instance",
        "example_20",
    )
    for file, name in zip(
        os.listdir(path),
        ["Delaunay_Flips", "Delaunay", "Greedy", "Iterative", "Random"],
    ):
        file_path = os.path.join(path, file)
        nodes = load_nodes_from_json(file_path)
        graph = Graph_Wrapper(nodes)
        sat_algorithm(graph)
        graph.name = file
        graph.show_and_save(save="figures/example", block=False, draw_name=False)
        logging.info(f"Graph {name} saved.")


if __name__ == "__main__":
    run_algo()
    # show_all_instanzes()
    # create_instance()
    # permute_instance()
    # generate_example()
    # draw_example()

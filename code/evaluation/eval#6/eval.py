import json
import logging
import os
import random
import socket
import uuid
from collections import defaultdict
from dataclasses import asdict

import slurminade
from dc_triangulation import SAT, Graph_Wrapper, Run_Algbench, SAT_Parameter

asdict
TIMEOUT = 300
path = os.path.join(os.path.dirname(__file__), "instances")
NUMBER_RUNS = 5  # Number of runs for each instance
# This is the entry point for the evaluation script
# It will run the Run_Instance class from run_algbench module


def get_key_from_pos(pos):
    assert (isinstance(pos, tuple)) and len(pos) == 2, (
        "Position must be a list of two elements, bus is",
        pos,
    )
    return f"{pos[0]}_{pos[1]}"


def load_data():
    """Load data from calculated_data.json file"""
    calculated_data_file = os.path.join(
        os.path.dirname(__file__), "calculated_data.json"
    )
    try:
        with open(calculated_data_file, "r") as f:
            data = json.load(f)
        logging.info(f"Loaded data from {calculated_data_file}")
        convertet_data = defaultdict(list)
        for item, value in data.items():
            for edge in value:
                assert isinstance(edge, list) and len(edge) == 2, (
                    "Each edge must be a list of two elements, but got",
                    edge,
                )
                assert isinstance(edge[0], list) and isinstance(edge[1], list), (
                    "Each edge must contain tuples, but got",
                    edge,
                )
                assert len(edge[0]) == 2 and len(edge[1]) == 2, (
                    "Each tuple in the edge must have two elements, but got",
                    edge,
                )
                convertet_data[item].append((tuple(edge[0]), tuple(edge[1])))
        return convertet_data
    except FileNotFoundError:
        logging.error(f"Could not find calculated_data.json at {calculated_data_file}")
        return {}
    except json.JSONDecodeError:
        logging.error(f"Could not parse JSON from {calculated_data_file}")
        return {}


data = load_data()


outer_parameter = {
    SAT: [
        {
            "timeout": TIMEOUT,
            "args": asdict(
                SAT_Parameter(
                    intersection=True,
                    degree_exact=True,
                )
            ),
        },
        {
            "timeout": TIMEOUT,
            "args": asdict(
                SAT_Parameter(
                    intersection=True,
                    degree_exact=True,
                    hack_eval6=0.1,  # das es bei show als eigener solver angezeigt wird, nicht schön aber funktioniert
                )
            ),
            "hack_eval_6": True,
            "hack_eval_6_data": data,
            "hack_eval_6_PERCENT": 0.1,
        },
        {
            "timeout": TIMEOUT,
            "args": asdict(
                SAT_Parameter(
                    intersection=True,
                    degree_exact=True,
                    hack_eval6=0.5,  # das es bei show als eigener solver angezeigt wird, nicht schön aber funktioniert
                )
            ),
            "hack_eval_6": True,
            "hack_eval_6_data": data,
            "hack_eval_6_PERCENT": 0.5,
        },
        {
            "timeout": TIMEOUT,
            "args": asdict(
                SAT_Parameter(
                    intersection=True,
                    degree_exact=True,
                    hack_eval6=0.8,  # das es bei show als eigener solver angezeigt wird, nicht schön aber funktioniert
                )
            ),
            "hack_eval_6": True,
            "hack_eval_6_data": data,
            "hack_eval_6_PERCENT": 0.8,
        },
        {
            "timeout": TIMEOUT,
            "args": asdict(
                SAT_Parameter(
                    intersection=True,
                    degree_exact=True,
                    hack_eval6=-0.1,  # das es bei show als eigener solver angezeigt wird, nicht schön aber funktioniert
                )
            ),
            "hack_eval_6": True,
            "hack_eval_6_data": data,
            "hack_eval_6_PERCENT": -0.1,
        },
        {
            "timeout": TIMEOUT,
            "args": asdict(
                SAT_Parameter(
                    intersection=True,
                    degree_exact=True,
                    hack_eval6=-0.5,  # das es bei show als eigener solver angezeigt wird, nicht schön aber funktioniert
                )
            ),
            "hack_eval_6": True,
            "hack_eval_6_data": data,
            "hack_eval_6_PERCENT": -0.5,
        },
        {
            "timeout": TIMEOUT,
            "args": asdict(
                SAT_Parameter(
                    intersection=True,
                    degree_exact=True,
                    hack_eval6=-0.8,  # das es bei show als eigener solver angezeigt wird, nicht schön aber funktioniert
                )
            ),
            "hack_eval_6": True,
            "hack_eval_6_data": data,
            "hack_eval_6_PERCENT": -0.8,
        },
    ]
}


RI = Run_Algbench(
    inst_path=path,
    outer_parameter=outer_parameter,
    figure_path=os.path.dirname(__file__),
)


# TODO iterativ_30 wurde nicht mit 0.1 und 0.5 gemacht


@slurminade.slurmify()
def run_solver_on_inst(key: str):
    solver, nodes, possible, inst, file_name = RI.get_solver_inst_from_runlist[key]
    parameters = RI.outer_parameter[solver]
    for parameter in parameters:
        ####################################################
        # hack für eval 6
        aktive_edges_percent = []
        not_aktive_edges_percent = []
        if parameter.get("hack_eval_6", False):
            try:
                if "hack_eval_6_data" not in parameter:
                    raise ValueError(
                        "hack_eval_6_data must be provided in the parameter."
                    )
                if "hack_eval_6_PERCENT" not in parameter:
                    raise ValueError(
                        "hack_eval_6_PERCENT must be provided in the parameter."
                    )
                data = parameter["hack_eval_6_data"]
                percent = parameter["hack_eval_6_PERCENT"]
                key = f"{inst}_{file_name}"
                if key not in data:
                    raise ValueError(f"No data found for instance {key}.")
                aktive_edges = data[key]
                all_edges = []
                for i in range(len(nodes)):
                    for j in range(i + 1, len(nodes)):
                        all_edges.append((nodes[i].pos, nodes[j].pos))

                not_aktive_edges = [
                    edge for edge in all_edges if edge not in aktive_edges
                ]
                if percent > 0:
                    anzahl = max(1, int(len(aktive_edges) * percent))
                    auswahl = random.sample(aktive_edges, anzahl)
                    aktive_edges_percent = auswahl
                if percent < 0:
                    anzahl = max(1, int(len(not_aktive_edges) * percent))
                    auswahl = random.sample(not_aktive_edges, anzahl)
                    not_aktive_edges_percent = auswahl

            except ValueError as e:
                logging.error(f"Error in hack_eval_6: {e}")
                continue
        ############################################

        for i in range(NUMBER_RUNS):
            run_seed = int(uuid.uuid4())
            random.seed(run_seed)  # Seed für Reproduzierbarkeit
            random.shuffle(nodes)  # Zufällige Reihenfolge der Knoten
            graph = Graph_Wrapper(nodes)
            pos_to_node_index = {
                get_key_from_pos(node.pos): i for i, node in enumerate(nodes)
            }  # Mapping von Position zu Knoten
            parameter["debug_set_edges"] = []
            for edge_pos in aktive_edges_percent:
                node1 = pos_to_node_index[get_key_from_pos(edge_pos[0])]
                node2 = pos_to_node_index[get_key_from_pos(edge_pos[1])]
                parameter["debug_set_edges"].append(
                    (min(node1, node2), max(node1, node2))
                )

            parameter["debug_exclude_edges"] = []
            for edge_pos in not_aktive_edges_percent:
                node1 = pos_to_node_index[get_key_from_pos(edge_pos[0])]
                node2 = pos_to_node_index[get_key_from_pos(edge_pos[1])]
                parameter["debug_exclude_edges"].append(
                    (min(node1, node2), max(node1, node2))
                )

            RI.benchmark.add(
                RI.create_benchmark_entry,
                solver_name=solver.NAME,
                parameter=parameter,
                instance_name=inst,
                file_name=file_name,
                run_number=i,
                host=socket.gethostname(),
                _run_seed=run_seed,
                _possible=possible,
                _solver_type=solver,
                _graph=graph,
            )


@slurminade.slurmify(mail_type="ALL")
def compress_results():
    # Compress the results to save significant disk space
    RI.compress()


# TODO auf glucard umstellen
if __name__ == "__main__":
    if True:
        slurminade.update_default_configuration(
            # Your supervisor will tell you these details
            partition="alg",  # Which partition to use. Usually group name.
            constraint="alggen03",  # Which workstations within the partition to use
            exclusive=True,  # To use all cores on a node exclusively
            mail_type="FAIL",  # Send mail on failure
            mail_user="f.alich@tu-braunschweig.de",  # Mail to this address
        )
        run_list = RI.get_run_list()
        for key in run_list:
            run_solver_on_inst.distribute(key)

        slurminade.join()
        compress_results.distribute()
    else:
        RI.show()

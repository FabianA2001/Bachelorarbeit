from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from solver.solver import Solver
from pysat.solvers import Solver as SatSolver
from pysat.formula import CNF
from pysat.card import CardEnc
import logging
import threading
from utils import time_function
import itertools
from dataclasses import dataclass

"""
wenn ein or im Name ist True das erste und False das zweite
sonnst aktiviert True den constrient
"""


@dataclass
class Parameter:
    solver_name: str = "glucose3"
    add_allEdges_or_exclude_edges: bool = True
    number_edges: bool = False
    intersection: bool = False
    all_edges: bool = False
    intersection_and_all_edges: bool = False
    degree_exact: bool = False
    degree_atleast: bool = False
    degree_subset: bool = False
    fix_hull: bool = False
    exclude_edges: bool = False


class SAT(Solver):
    NAME = "SAT"

    def __init__(self, graph: Graph_Wrapper) -> None:
        super().__init__(graph)
        self.name = self.NAME

    def setup(self, parameter: Parameter):
        self.graph.add_all_possible_edges(default_for_active=False)
        if not parameter.add_allEdges_or_exclude_edges:
            edges = self.graph.exclude_edge_partition
            for edge in edges:
                try:
                    self.graph.remove_edge(edge)
                except ValueError:
                    pass
        self.edges = self.graph.get_all_edges()
        self.edges_to_index = {edge: i for i, edge in enumerate(self.edges)}
        self.all_vars = list(range(1, len(self.edges) + 1))
        logging.info(
            f"Anzahl Kanten: {len(self.edges)}, Anzahl Variablen: {len(self.all_vars)}"
        )

    def get_index(self, edge) -> int:
        if edge in self.edges_to_index:
            return self.edges_to_index[edge] + 1
        if (edge[1], edge[0]) in self.edges_to_index:
            return self.edges_to_index[(edge[1], edge[0])] + 1
        return -1

    def get_edge(self, index) -> tuple[int, int]:
        return self.edges[index - 1]

    def number_edge_constraint(self):
        cnf = self.formula_number_vars(
            self.all_vars,
            self.graph.get_number_edges_in_Triangulation(),
            exact_atleast=True,
        )
        self.solver.append_formula(cnf)
        if self.reach_timeout():
            raise TimeoutError()

    def intersection_constraint(self):
        intersection = self.graph.get_all_intersections(self.timeout_error)
        for edge, other_edge in intersection:
            edge_index = self.get_index(edge)
            other_edge_index = self.get_index(other_edge)
            if edge_index == -1 or other_edge_index == -1:
                continue
            self.solver.add_clause([-edge_index, -other_edge_index])
        self.timeout_error()

    def alle_edges_constraint(self):
        edges = self.graph.get_all_edges()
        for edge in edges:
            intersection = self.graph.get_intersections_with_all_edges(edge)
            self.solver.add_clause(
                [self.get_index(edge)]
                + [self.get_index(other_edge) for other_edge in intersection]
            )

    def alle_edges_and_intersection_constraint(self):
        edges = self.graph.get_all_edges()
        for edge in edges:
            intersections = self.graph.get_intersections_with_all_edges(edge)
            self.solver.add_clause(
                [self.get_index(edge)]
                + [self.get_index(other_edge) for other_edge in intersections]
            )
            for intersect in intersections:
                self.solver.add_clause(
                    [-self.get_index(edge), -self.get_index(intersect)]
                )

    def degree_constraint(self, exact_atleast=True):
        for node in self.graph.get_all_nodes():
            degree = self.graph.get_desired_degree_node(node)
            if degree == -1:
                continue
            edges = self.graph.get_edges_of_node(node)
            cnf = self.formula_number_vars(
                [self.get_index(edge) for edge in edges],
                degree,
                exact_atleast=exact_atleast,
            )
            self.solver.append_formula(cnf)
            if self.reach_timeout():
                raise TimeoutError()

    def degree_subset_constraint(self):
        for node in self.graph.get_all_nodes():
            degree = self.graph.get_desired_degree_node(node)
            edges = [
                self.get_index(edge) for edge in self.graph.get_edges_of_node(node)
            ]
            for subset in itertools.combinations(edges, len(edges) - (degree - 1)):
                self.solver.add_clause(subset)
                self.timeout_error()

    def set_hull_fix_constraint(self):
        hull_edges = self.graph.get_hull_edges()
        if len(hull_edges) == 0:
            return

        for edge in hull_edges:
            index = self.get_index(edge)
            # Setze die Kante als aktiv
            self.solver.add_clause([index])
        if self.reach_timeout():
            raise TimeoutError()

    def exclude_edges_constraint(self):
        for edge in self.graph.exclude_edge_partition:
            if edge in self.graph.impossible_edges:
                continue
            index = self.get_index(edge)
            # Setze die Kante als inaktiv
            self.solver.add_clause([-index])

    def formula_number_vars(self, vars, n, exact_atleast=True):
        # CNF-Formel erstellen
        cnf = CNF()
        # Cardinality Constraint: genau n Variablen aus "vars" sind True
        assert len(vars) >= n
        used = (
            max(
                self.solver.nof_vars(),  # type: ignore
                len(self.all_vars),
            )
            + 1
        )
        if exact_atleast:
            enc = CardEnc.equals(lits=vars, bound=n, top_id=used)
        else:
            enc = CardEnc.atleast(lits=vars, bound=n, top_id=used)
        cnf.extend(enc.clauses)
        return cnf
        # TODO andere self solver testen, anstatt glucose42

    def pre_solve(self, parameter_data: Parameter) -> None:
        self.solver = SatSolver(name=parameter_data.solver_name)
        if not hasattr(self.solver, "interrupt"):
            raise RuntimeError(
                "The solver does not support interruption. "
                "Please use a different solver that supports this feature."
            )
        self.setup(parameter_data)
        if parameter_data.number_edges:
            time_function(self.number_edge_constraint)()
        if parameter_data.intersection:
            time_function(self.intersection_constraint)()
        if parameter_data.all_edges:
            time_function(self.alle_edges_constraint)()
        if parameter_data.intersection_and_all_edges:
            time_function(self.alle_edges_and_intersection_constraint)()
        if parameter_data.degree_exact:
            time_function(self.degree_constraint)(exact_atleast=True)
        if parameter_data.degree_atleast:
            time_function(self.degree_constraint)(exact_atleast=False)
        if parameter_data.degree_subset:
            time_function(self.degree_subset_constraint)()
        if parameter_data.fix_hull:
            time_function(self.set_hull_fix_constraint)()
        if parameter_data.exclude_edges:
            time_function(self.exclude_edges_constraint)()

    def _actual_solver(self, parameter: dict) -> dict:
        if not isinstance(parameter, dict):
            raise TypeError("Parameter must be a dictionary.")
        args = parameter.get("args", None)
        assert args is not None, "Parameter 'args' must be provided in the dictionary."
        parameter_data: Parameter = Parameter(**(args))

        try:
            self.time_pre_solve(self.pre_solve)(parameter_data)
            if "timeout" not in parameter:
                raise ValueError("Timeout parameter is missing.")

            timeout = parameter["timeout"]
            if not isinstance(timeout, (int, float)):
                raise TypeError("Timeout must be an integer or float.")

            result = [None]

            if timeout == -1:
                result[0] = self.time_solver(self.solver.solve)()
            else:
                logging.info("start solving")

                def run_solver():
                    result[0] = self.time_solver(self.solver.solve_limited)(  # type: ignore
                        expect_interrupt=True
                    )

                thread = threading.Thread(target=run_solver)
                thread.start()
                thread.join(self.get_remaining_time())
                if thread.is_alive():
                    self.solver.interrupt()
                    thread.join()
                    raise TimeoutError()

            model = self.solver.get_model()
            assert model is not None, "Model should not be None"
            for var in self.all_vars:
                if var in model:
                    self.graph.activate_edge(self.get_edge(var))

            return {
                "success": result[0],
            }
        except TimeoutError:
            logging.warning(f"{self.name} timed out.")
            return {
                "success": False,
            }

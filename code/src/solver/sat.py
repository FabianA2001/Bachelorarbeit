from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from solver.solver import Solver
from pysat.solvers import Solver as SatSolver
from pysat.formula import CNF
from pysat.card import CardEnc
import logging
import threading
from utils import time_function
import itertools


class SAT(Solver):
    NAME = "SAT"

    def __init__(self, graph: Graph_Wrapper) -> None:
        super().__init__(graph)
        self.name = self.NAME
        self.graph.add_all_possible_edges(default_for_active=False)
        self.edges = self.graph.get_all_edges()
        self.edges_to_index = {edge: i for i, edge in enumerate(self.edges)}
        self.all_vars = list(range(1, len(self.edges) + 1))

    def get_index(self, edge) -> int:
        if edge in self.edges_to_index:
            return self.edges_to_index[edge] + 1
        return self.edges_to_index[(edge[1], edge[0])] + 1

    def get_edge(self, index) -> tuple[int, int]:
        return self.edges[index - 1]

    def intersection_constraint(self):
        intersection = self.graph.get_all_intersections(self.timeout_error)
        for edge, other_edge in intersection:
            if (
                edge in self.graph.impossible_edges
                or (edge[1], edge[0]) in self.graph.impossible_edges
            ):
                continue
            if (
                other_edge in self.graph.impossible_edges
                or (other_edge[1], other_edge[0]) in self.graph.impossible_edges
            ):
                continue
            self.solver.add_clause([-self.get_index(edge), -self.get_index(other_edge)])
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
        for node in self.graph.get_all_nodes_name():
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
        for node in self.graph.get_all_nodes_name():
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

    def _actual_solver(self, parameter: dict) -> dict:
        if not isinstance(parameter, dict):
            raise TypeError("Parameter must be a dictionary.")

        try:
            self.solver = SatSolver(name="glucose3")
            if not hasattr(self.solver, "interrupt"):
                raise RuntimeError(
                    "The solver does not support interruption. "
                    "Please use a different solver that supports this feature."
                )
            if "version" not in parameter:
                raise ValueError("Version parameter is missing.")
            if parameter.get("version") == 0.1:
                time_function(self.intersection_constraint)()
                self.degree_constraint()
            elif parameter.get("version") == 0.2:
                time_function(self.intersection_constraint)()
                self.set_hull_fix_constraint()
                self.degree_constraint()
            elif parameter.get("version") == 0.3:
                time_function(self.intersection_constraint)()
                self.degree_constraint()
                self.set_hull_fix_constraint()
                time_function(self.alle_edges_constraint)()
            elif parameter.get("version") == 0.4:
                self.degree_constraint()
                self.set_hull_fix_constraint()
                time_function(self.alle_edges_and_intersection_constraint)()
            elif parameter.get("version") == 0.5:
                time_function(self.degree_subset_constraint)()
                self.set_hull_fix_constraint()
                time_function(self.intersection_constraint)()
            else:
                time_function(self.degree_constraint)(False)
                self.set_hull_fix_constraint()
                time_function(self.intersection_constraint)()

            if "timeout" not in parameter:
                raise ValueError("Timeout parameter is missing.")

            timeout = parameter["timeout"]
            if not isinstance(timeout, (int, float)):
                raise TypeError("Timeout must be an integer or float.")

            result = [None]

            if timeout == -1:
                result[0] = time_function(self.solver.solve)()
            else:
                logging.info("start solving")

                def run_solver():
                    result[0] = time_function(self.solver.solve_limited)(  # type: ignore
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
            return {
                "success": False,
            }

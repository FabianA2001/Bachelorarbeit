from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from solver.solver import Solver
from pysat.solvers import Solver as SatSolver
from pysat.formula import CNF
from pysat.card import CardEnc
import logging
import threading


class TimeoutError(Exception):
    """Custom exception for timeout errors."""

    pass


class SAT(Solver):
    NAME = "SAT"
    # TODO Paper von Discord zur Intersection constraind

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

    def get_edge(self, index) -> tuple[str, str]:
        return self.edges[index - 1]

    def intersection_constraint(self):
        for edge in self.edges:
            intersections = self.graph.get_intersections_with_all_edges(
                edge, check_if_active=False
            )
            for intersection in intersections:
                self.solver.add_clause(
                    [-self.get_index(edge), -self.get_index(intersection)]
                )

            if self.reach_timeout():
                raise TimeoutError()

    def degree_constraint(self):
        for node in self.graph.get_all_nodes_name():
            degree = self.graph.get_degree_of_node(node)
            if degree == -1:
                continue
            edges = self.graph.get_edges_of_node(node)
            cnf = self.formula_number_vars(
                [self.get_index(edge) for edge in edges], degree
            )
            self.solver.append_formula(cnf)
            if self.reach_timeout():
                raise TimeoutError()

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

    # TODO subsets bilden und statt dieser Funktion nutzen FOTO(1)
    def formula_number_vars(self, vars, n):
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
        enc = CardEnc.equals(lits=vars, bound=n, top_id=used)
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
                self.intersection_constraint()
                self.degree_constraint()
            elif parameter.get("version") == 0.2:
                self.intersection_constraint()
                self.degree_constraint()
                self.set_hull_fix_constraint()
            else:
                raise ValueError(
                    f"Version {parameter.get('version')} is not supported for self solver."
                )

            if "timeout" not in parameter:
                raise ValueError("Timeout parameter is missing.")

            timeout = parameter["timeout"]
            if not isinstance(timeout, (int, float)):
                raise TypeError("Timeout must be an integer or float.")

            result = [None]

            if timeout == -1:
                result[0] = self.solver.solve()
            else:
                logging.info("start solving")

                def run_solver():
                    result[0] = self.solver.solve_limited(expect_interrupt=True)

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

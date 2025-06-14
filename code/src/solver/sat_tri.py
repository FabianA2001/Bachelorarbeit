from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from solver.solver import Solver
from pysat.solvers import Solver as SatSolver
from pysat.formula import CNF
from pysat.card import CardEnc
import logging
import threading
from utils import time_function


class SAT(Solver):
    NAME = "SAT"

    def __init__(self, graph: Graph_Wrapper) -> None:
        super().__init__(graph)
        self.name = self.NAME
        self.aktive_constrinsts = ""
        self.tris = self.graph.get_all_triangles()
        self.all_vars = list(range(1, len(self.tris) + 1))
        self.tri_to_index = {tri: i for i, tri in enumerate(self.tris)}

    def get_index(self, tri) -> int:
        tri = tuple(sorted(tri))
        return self.tri_to_index[tri] + 1

    def get_edge(self, index) -> tuple[int, int]:
        return self.tris[index - 1]

    def atleast_tri_constraint(self, k: int):
        self.aktive_constrinsts += "atleast_tri_(int), "
        if k < 1:
            raise ValueError("k must be at least 1.")
        if k > len(self.tris):
            raise ValueError("k is larger than the number of triangles.")
        cnf = self.formula_number_vars(
            vars=self.all_vars,
            n=k,
            exact_atleast=False,
        )
        self.solver.append_formula(cnf)
        self.timeout_error()

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
                pass
            elif parameter.get("version") == 0.2:
                pass
            else:
                pass
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
            # for var in self.all_vars:
            #     if var in model:
            #         self.graph.activate_edge(self.get_edge(var))

            return {
                "success": result[0],
                "info": self.aktive_constrinsts,
            }
        except TimeoutError:
            logging.warning(f"{self.name} timed out.")
            return {
                "success": False,
                "info": self.aktive_constrinsts,
            }

from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from solver.solver import Solver, Solution, Parameter
from pysat.solvers import Solver as SatSolver
from pysat.formula import CNF
from pysat.card import CardEnc
import logging
import multiprocessing
import queue


class TimeoutError(Exception):
    """Custom exception for timeout errors in solvers."""

    pass


class SAT(Solver):
    NAME = "SAT"

    # TODO Paper von Discord zur Intersection constraind
    # TODO Hülle vorher entfernen und aus degree rausrechnen
    def __init__(self, graph: Graph_Wrapper) -> None:
        super().__init__(graph)
        self.name = self.NAME
        self.graph.add_all_possible_edges(default_for_active=True)
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
            intersections = self.graph.get_intersections_with_all_edges(edge)
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

    def handel_queue(self, result_queue) -> Solution:
        if result_queue.empty():
            self.graph.clear_all_edges()
            logging.warning("queue ist empty")
            return Solution(False)

        vars = []
        success = False
        while not result_queue.empty():
            result = result_queue.get()
            if isinstance(result, list):
                if all(isinstance(i, int) for i in result):
                    vars = result
                    continue

            if isinstance(result, bool):
                success = result
                break

            assert False, "Result is not a tuple or bool, result: {}".format(result)

        self.graph.clear_all_edges()
        if not len(vars) > 0:
            logging.warning("No edges found in queue")
            return Solution(success)

        for var in vars:
            edge = self.get_edge(var)
            self.graph.add_edge(edge[0], edge[1], active=True)
        return Solution(success)

    def __handel_solver_with_timeout(self, timeout: float) -> Solution:
        result_queue = multiprocessing.Queue()
        process = multiprocessing.Process(
            target=self.prcess_solver, args=(result_queue, self.solver, self.all_vars)
        )
        process.start()
        process.join(timeout if timeout > 0 else None)

        if process.is_alive():
            process.terminate()
            process.join()
            self.success = False
        return self.handel_queue(result_queue)

    def __handel_solver_without_timeout(self) -> Solution:
        result_queue = queue.Queue()
        self.prcess_solver(result_queue, self.solver, self.all_vars)
        self.graph.clear_all_edges()
        return self.handel_queue(result_queue)

    @staticmethod
    def prcess_solver(queue, solver, all_vars):
        if not solver.solve():
            queue.put(False)
            return

        model = solver.get_model()
        aktive_vars = []
        assert model is not None, "Model should not be None"
        for var in all_vars:
            if var in model:
                aktive_vars.append(var)
        logging.info(len(aktive_vars))
        queue.put(aktive_vars)
        queue.put(True)

        # TODO andere sat solver testen, anstatt glucose42

    def _actual_solver(self, parameter: Parameter) -> Solution:
        try:
            self.solver = SatSolver(name="glucose42")
            self.intersection_constraint()
            self.degree_constraint()
            # TODO Remaining Time zum solver hinzufügen

            if self.reach_timeout():
                raise TimeoutError()

            if self.timeout < 0:
                result = self.__handel_solver_without_timeout()
            else:
                result = self.__handel_solver_with_timeout(self.get_remaining_time())
            return result
        except TimeoutError:
            self.graph.clear_all_edges()
            logging.warning("abbruch wegen timeout")
            return Solution(False)

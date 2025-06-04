from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from solver.solver import Solver
from pysat.solvers import Solver as SatSolver
from pysat.formula import CNF
from pysat.card import CardEnc
import logging


class SAT(Solver):
    VERSION = "0.1"
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
            # TODO nur als eine Klausel
            for intersection in intersections:
                self.solver.add_clause(
                    [-self.get_index(edge), -self.get_index(intersection)]
                )

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

    # TODO andere sat solver testen, anstatt glucose42
    def _actual_solver(self, timeout, queue) -> None:
        self.solver = SatSolver(name="glucose42")
        # cnf = self.formula_number_vars(
        #     self.all_vars, self.graph.get_number_edges_in_Triangulation()
        # )
        # self.solver.append_formula(cnf)
        self.intersection_constraint()
        self.degree_constraint()
        # SAT lösen
        if self.solver.solve():
            quere_edges = []
            model = self.solver.get_model()
            assert model is not None, "Model should not be None"
            for var in self.all_vars:
                if var in model:
                    edge = self.get_edge(var)
                    quere_edges.append(edge)
            queue.put(quere_edges)
            queue.put(True)
            return

        else:
            logging.error("SAT Solver could not find a solution.")
            queue.put(False)
            return

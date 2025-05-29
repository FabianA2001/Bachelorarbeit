from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from solver.solver import Solver
from pysat.solvers import Solver as SatSolver
from pysat.formula import CNF
from pysat.card import CardEnc


class SAT(Solver):
    def __init__(self, graph: Graph_Wrapper) -> None:
        super().__init__(graph)
        self.name = "SAT"
        self.version = "0.1"
        self.graph.add_all_possible_edges(default_for_active=True)
        self.edges = self.graph.get_all_edges()
        self.edges_to_index = {edge: i for i, edge in enumerate(self.edges)}

    def get_index(self, edge) -> int:
        return self.edges_to_index[edge] + 1

    def get_edge(self, index) -> tuple[str, str]:
        return self.edges[index - 1]

    def intersection_constraint(self):
        for edge in self.edges:
            intersections = self.graph.get_intersections_with_all_edges(edge)
            for intersection in intersections:
                self.solver.add_clause(
                    [-self.get_index(edge), -self.get_index(intersection)]
                )

    def formula_number_vars(self, n):
        # CNF-Formel erstellen
        cnf = CNF()
        # Cardinality Constraint: genau n Variablen aus "vars" sind True
        self.vars = list(range(1, len(self.edges) + 1))
        assert len(self.vars) >= n
        enc = CardEnc.equals(lits=self.vars, bound=n, encoding=1)
        cnf.extend(enc.clauses)
        return cnf

    def _actual_solver(self, timeout, queue) -> None:
        cnf = self.formula_number_vars(self.graph.get_number_edges_in_Triangulation())

        self.solver = SatSolver(name="glucose3", bootstrap_with=cnf)
        self.intersection_constraint()

        # SAT lösen
        if self.solver.solve():
            quere_edges = []
            model = self.solver.get_model()
            assert model is not None, "Model should not be None"
            for var in self.vars:
                if var in model:
                    edge = self.get_edge(var)
                    quere_edges.append(edge)
            queue.put(quere_edges)
            queue.put(self.graph.check_if_triangulation_with_degree_constraint())
            return

        else:
            queue.put(False)
            return

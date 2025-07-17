from dataclasses import dataclass

from pysat.card import CardEnc, EncType

from ..cpp._cpp_bindings import cadical_wrapper
from ..graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from .solver import Solver


@dataclass
class Parameter:
    intersection: bool = False
    degree: bool = False


class Cadical(Solver):
    NAME = "Cadical"

    def __init__(self, graph: Graph_Wrapper) -> None:
        super().__init__(graph)
        self.logger.warning("Kein Timeout")
        self.name = self.NAME

    def setup(self, parameter: Parameter):
        self.graph.add_all_possible_edges(default_for_active=False)
        self.edges = self.graph.get_all_edges()
        self.max_used = len(self.edges)
        self.edges_to_index = {edge: i for i, edge in enumerate(self.edges)}
        self.clauses = []

    def get_index(self, edge) -> int:
        if (min(edge[0], edge[1]), max(edge[0], edge[1])) in self.edges_to_index:
            return self.edges_to_index[edge] + 1
        return -1

    def intersection_constraint(self):
        intersection_all = self.graph.get_all_intersections_cpp(self.timeout_error)
        for edge, intersections in intersection_all.items():
            edge_index = self.get_index(edge)
            for intersection in intersections:
                other_edge_index = self.get_index(intersection)
                if edge_index == -1 or other_edge_index == -1:
                    continue
                self.clauses.append([-edge_index, -other_edge_index])

    def formula_number_vars(
        self, vars, n, exact_atleast=True, encoding: int = EncType.seqcounter
    ):
        # CNF-Formel erstellen
        # Cardinality Constraint: genau n Variablen aus "vars" sind True
        assert len(vars) >= n
        if exact_atleast:
            enc = CardEnc.equals(
                lits=vars, bound=n, top_id=self.max_used + 1, encoding=encoding
            )
        else:
            enc = CardEnc.atleast(
                lits=vars, bound=n, top_id=self.max_used + 1, encoding=encoding
            )

        for clause in enc.clauses:
            for literal in clause:
                self.max_used = max(self.max_used, abs(literal))
        return enc.clauses

    def degree_constraint(self, exact_atleast=True, encoding: int = EncType.seqcounter):
        for node in self.graph.get_all_nodes():
            degree = self.graph.get_desired_degree_node(node)
            if degree == -1:
                continue
            edges = self.graph.get_edges_of_node(node)
            cnf = self.formula_number_vars(
                [self.get_index(edge) for edge in edges],
                degree,
                exact_atleast=exact_atleast,
                encoding=encoding,
            )
            for clause in cnf:
                self.clauses.append(clause)

    def pre_solve(self, parameter: Parameter) -> None:
        self.setup(parameter)
        if parameter.intersection:
            self.intersection_constraint()
        if parameter.degree:
            self.degree_constraint(exact_atleast=True, encoding=EncType.seqcounter)

    def _actual_solver(self, parameter_raw: dict) -> dict:
        if self.graph is None:
            raise ValueError("Graph is not set. Please set the graph before solving.")

        assert self.graph.get_all_edges() == [], (
            "Graph is not empty. Please clear the graph before solving."
        )

        if not isinstance(parameter_raw, dict):
            raise TypeError("Parameter must be a dictionary.")
        args = parameter_raw.get("args", None)
        assert args is not None, "Parameter 'args' must be provided in the dictionary."
        parameter: Parameter = Parameter(**(args))

        self.time_pre_solve(self.pre_solve)(parameter)

        vars, debug_vars = self.time_solver(cadical_wrapper)(
            self.max_used, self.clauses
        )

        for i in range(len(self.edges)):
            if vars[i] == 1:
                self.logger.info(f"var{i}: {vars[i]}")
                self.graph.activate_edge(self.edges[i])
            else:
                self.logger.info(f"var{i}: {vars[i]}")

        return {
            "success": True,
            "debug_vars": debug_vars,
        }

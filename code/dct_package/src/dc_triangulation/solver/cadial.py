from collections import defaultdict
from dataclasses import dataclass

from pysat.card import CardEnc, EncType

from ..cpp._cpp_bindings import cadical_wrapper
from ..graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from .solver import Solver


@dataclass
class Parameter:
    intersection: bool = False
    degree: bool = False
    fix_hull: bool = False
    all_edges: bool = False
    exclude_edges: bool = True
    save_state: bool = False
    optimize_propagation: bool = False


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

    def set_hull_fix_constraint(self):
        hull_edges = self.graph.get_hull_edges()
        if len(hull_edges) == 0:
            return

        for edge in hull_edges:
            index = self.get_index(edge)
            # Setze die Kante als aktiv
            self.clauses.append([index])

    def alle_edges_constraint(self):
        intersection_all = self.graph.get_all_intersections_cpp(self.timeout_error)
        # intersection_all = self.graph.get_all_intersections_n2()
        for edge, intersections in intersection_all.items():
            self.clauses.append(
                [self.get_index(edge)]
                + [self.get_index(other_edge) for other_edge in intersections]
            )

    def exclude_edges_constraint(self):
        for edge in self.graph.exclude_edges:
            index = self.get_index(edge)
            # Setze die Kante als inaktiv
            self.clauses.append([-index])

    def pre_solve(self, parameter: Parameter) -> None:
        self.setup(parameter)
        if parameter.intersection:
            self.intersection_constraint()
        if parameter.degree:
            self.degree_constraint(exact_atleast=True, encoding=EncType.seqcounter)
        if parameter.fix_hull:
            self.set_hull_fix_constraint()
        if parameter.all_edges:
            self.alle_edges_constraint()
        if parameter.exclude_edges:
            self.exclude_edges_constraint()

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

        node_to_sdegree = {}
        for node in self.graph.get_all_nodes():
            pos = self.graph.get_pos_from_node(node)
            pos_str = f"{pos[0]},{pos[1]}"
            sdegree = self.graph.get_desired_degree_node(node)
            node_to_sdegree[pos_str] = sdegree

        edges_as_pos = []
        for edge in self.edges:
            pos1 = self.graph.get_pos_from_node(edge[0])
            pos2 = self.graph.get_pos_from_node(edge[1])
            edges_as_pos.append((pos1, pos2))
        nodes_as_pos = [
            self.graph.get_pos_from_node(node) for node in self.graph.get_all_nodes()
        ]
        # print(self.edges[108 - 1])
        # return {}
        intersections = defaultdict(list)
        for edge, intersection in self.graph.get_all_intersections_cpp().items():
            edge_index = self.get_index(edge)
            if edge_index == -1:
                continue
            for other_edge in intersection:
                other_edge_index = self.get_index(other_edge)
                if other_edge_index == -1:
                    continue
                intersections[edge_index].append(other_edge_index)

        vars, debug_vars, counter = self.time_solver(cadical_wrapper)(
            self.max_used,
            len(self.edges),
            self.clauses,
            nodes_as_pos,
            edges_as_pos,
            node_to_sdegree,
            intersections,
            parameter.save_state,
            parameter.optimize_propagation,
        )

        sucess = False
        if len(vars) > 1:
            sucess = True
            for i in range(len(self.edges)):
                if vars[i] == 1:
                    self.graph.activate_edge(self.edges[i])

        return {
            "success": sucess,
            "debug_vars": debug_vars,
            "counter": counter,
        }

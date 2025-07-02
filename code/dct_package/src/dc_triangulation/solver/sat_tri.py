import itertools
import threading
from dataclasses import dataclass

import shapely
from pysat.card import CardEnc
from pysat.formula import CNF
from pysat.solvers import Solver as SatSolver

from ..graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from ..solver.solver import Solver
from ..utils import time_function


@dataclass
class Parameter:
    solver_name: str = "glucose3"
    add_allEdges_or_exlucde_edges: bool = True
    number_tri: bool = False
    intersection: bool = False
    degree: bool = False
    exclude_edges: bool = False


class SAT_TRI(Solver):
    NAME = "SAT_TRI"

    def __init__(self, graph: Graph_Wrapper) -> None:
        super().__init__(graph)
        self.name = self.NAME

    def setup(self, parameter: Parameter):
        self.graph.add_all_possible_edges(default_for_active=False)
        if not parameter.add_allEdges_or_exlucde_edges:
            edges = self.graph.exclude_edge_partition
            for edge in edges:
                try:
                    self.graph.remove_edge(edge)
                except ValueError:
                    pass

        self.tris = self.graph.get_all_triangles()
        self.tris_as_point = [
            (
                self.graph.get_point_from_node(node1),
                self.graph.get_point_from_node(node2),
                self.graph.get_point_from_node(node3),
            )
            for node1, node2, node3 in self.graph.get_all_triangles()
        ]
        # hier speichern
        self.all_vars = list(range(1, len(self.tris) + 1))
        self.tri_to_index = {tri: i for i, tri in enumerate(self.tris)}
        self.point_to_index = {tri: i for i, tri in enumerate(self.tris_as_point)}

        # Mapping von Kanten zu Dreiecken für schnelle Suche
        self.edge_to_triangles = {}
        for i, tri in enumerate(self.tris):
            # Alle drei Kanten des Dreiecks
            edges = [
                tuple(sorted([tri[0], tri[1]])),
                tuple(sorted([tri[1], tri[2]])),
                tuple(sorted([tri[0], tri[2]])),
            ]
            for edge in edges:
                if edge not in self.edge_to_triangles:
                    self.edge_to_triangles[edge] = []
                self.edge_to_triangles[edge].append(
                    i + 1
                )  # +1 für 1-basierte Indizierung

        self.solver = SatSolver(name=parameter.solver_name)
        if not hasattr(self.solver, "interrupt"):
            raise RuntimeError(
                "The solver does not support interruption. "
                "Please use a different solver that supports this feature."
            )

        if parameter.number_tri:
            self.number_tri_constraint()

        if parameter.intersection:
            time_function(self.intersection_constraint, self.logger)()

        if parameter.degree:
            time_function(self.degree_constraint, self.logger)()

        if parameter.exclude_edges:
            time_function(self.exclude_triangles_constraint)()

    def get_index(self, tri_pos) -> int:
        if not (isinstance(tri_pos, tuple) and len(tri_pos) == 3):
            raise ValueError("tri_pos must be a tuple of length 3.")
        if all(isinstance(x, int) for x in tri_pos):
            tri = tuple(sorted(tri_pos))
            return self.tri_to_index[tri] + 1
        if all(isinstance(x, shapely.Point) for x in tri_pos):
            return self.point_to_index[tri_pos] + 1
        assert False, "tri_pos must be a tuple of length 2 or 3."

    def get_tri(self, index) -> tuple[int, int]:
        return self.tris[index - 1]

    @staticmethod
    def triangles_intersect(
        tri1: tuple[shapely.Point, shapely.Point, shapely.Point],
        tri2: tuple[shapely.Point, shapely.Point, shapely.Point],
    ) -> bool:
        tri1_poly = shapely.Polygon(tri1)
        tri2_poly = shapely.Polygon(tri2)
        assert tri1_poly.is_valid, "Triangle 1 is not a valid polygon."
        assert tri2_poly.is_valid, "Triangle 2 is not a valid polygon."
        return tri1_poly.intersects(tri2_poly) and not tri1_poly.touches(tri2_poly)

    def number_tri_constraint(self):
        cnf = self.formula_number_vars(
            vars=self.all_vars,
            n=self.graph.get_number_tris_in_Triangulation(),
            exact_atleast=True,
        )
        self.solver.append_formula(cnf)
        self.timeout_error()

    def intersection_constraint(self):
        for tri1, tri2 in itertools.combinations(self.tris_as_point, 2):
            # for tri1, tri2 in [(self.tris_as_point[3], self.tris_as_point[0])]:
            if self.triangles_intersect(tri1, tri2):
                index1 = self.get_index(tri1)
                index2 = self.get_index(tri2)
                self.solver.add_clause([-index1, -index2])
        self.timeout_error()

    def exclude_triangles_constraint(self):
        for edge in self.graph.exclude_edge_partition:
            tris = self.get_triangles_from_edge(edge)
            for tri in tris:
                self.solver.add_clause([-tri])

    def degree_constraint(self):
        hull = self.graph.get_hull_nodes()
        for node in self.graph.get_all_nodes():
            tris = self.graph.get_triangles_from_node(node)
            degree = self.graph.get_desired_degree_node(node)
            if node in hull:
                degree -= 1
            cnf = self.formula_number_vars(
                vars=[self.get_index(tri) for tri in tris],
                n=degree,
                exact_atleast=False,
            )
            self.solver.append_formula(cnf)

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
            args = parameter.get("args", None)
            assert args is not None, (
                "Args must be provided in the parameter dictionary."
            )
            parameter_data: Parameter = Parameter(**(args))
            self.time_pre_solve(self.setup)(parameter_data)

            if "timeout" not in parameter:
                raise ValueError("Timeout parameter is missing.")

            timeout = parameter["timeout"]
            if not isinstance(timeout, (int, float)):
                raise TypeError("Timeout must be an integer or float.")

            result = [None]

            if timeout == -1:
                result[0] = self.time_solver(self.solver.solve)()
            else:
                self.logger.info("start solving")

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
            if model is not None:
                for var in self.all_vars:
                    if var in model:
                        tri = self.get_tri(var)
                        for node1, node2 in itertools.combinations(tri, 2):
                            self.graph.activate_edge((node1, node2))
                            # print(f"Activating edge: {node1} - {node2}")
                        # self.graph.activate_edge(self.get_edge(var))

            return {
                "success": result[0],
            }
        except TimeoutError:
            self.logger.warning(f"{self.name} timed out.")
            return {
                "success": False,
            }

    def get_triangles_from_edge(self, edge: tuple[int, int]) -> list[int]:
        """
        Gibt alle Dreiecks-Indizes zurück, die die gegebene Kante enthalten.

        Args:
            edge: Tuple von zwei Knoten (wird automatisch sortiert)

        Returns:
            Liste der Dreiecks-Indizes (1-basiert)
        """
        sorted_edge = tuple(sorted(edge))
        return self.edge_to_triangles.get(sorted_edge, [])

from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
import shapely
from solver.solver import Solver
from pysat.solvers import Solver as SatSolver
from pysat.formula import CNF
from pysat.card import CardEnc
import logging
import threading
from utils import time_function
import itertools
from dataclasses import dataclass


@dataclass
class Parameter:
    solver_name: str = "glucose3"
    add_allEdges_or_exlucde_edges: bool = True
    number_tri: bool = False
    intersection: bool = False
    degree: bool = False


class SAT_TRI(Solver):
    NAME = "SAT"

    def __init__(self, graph: Graph_Wrapper) -> None:
        super().__init__(graph)
        self.name = self.NAME

    def setup(self, parameter: Parameter):
        self.graph.add_all_possible_edges(default_for_active=False)
        if not parameter.add_allEdges_or_exlucde_edges:
            edges = self.graph.exclude_edge_partition()
            for edge in edges:
                try:
                    self.graph.remove_edge(edge)
                except ValueError:
                    pass

        self.tris = self.graph.get_all_triangles()
        logging.warning("Dreiecke sind teilweise nicht leer, warten auf ccp für fix")
        self.tris_as_point = [
            (
                self.graph.get_point_from_node(node1),
                self.graph.get_point_from_node(node2),
                self.graph.get_point_from_node(node3),
            )
            for node1, node2, node3 in self.graph.get_all_triangles()
        ]
        self.all_vars = list(range(1, len(self.tris) + 1))
        self.tri_to_index = {tri: i for i, tri in enumerate(self.tris)}
        self.point_to_index = {tri: i for i, tri in enumerate(self.tris_as_point)}

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
            parameter_data: Parameter = Parameter(**(parameter.get("args", {})))
            self.setup(parameter_data)

            self.solver = SatSolver(name=parameter_data.solver_name)
            if not hasattr(self.solver, "interrupt"):
                raise RuntimeError(
                    "The solver does not support interruption. "
                    "Please use a different solver that supports this feature."
                )

            if parameter_data.number_tri:
                self.number_tri_constraint()

            if parameter_data.intersection:
                time_function(self.intersection_constraint)()

            if parameter_data.degree:
                time_function(self.degree_constraint)()

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
                    tri = self.get_tri(var)
                    for node1, node2 in itertools.combinations(tri, 2):
                        self.graph.activate_edge((node1, node2))
                        # print(f"Activating edge: {node1} - {node2}")
                    # self.graph.activate_edge(self.get_edge(var))

            return {
                "success": result[0],
            }
        except TimeoutError:
            logging.warning(f"{self.name} timed out.")
            return {
                "success": False,
            }

from solver.solver import Solver
from ortools.sat.python import cp_model
from graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
import logging
from utils import time_function


class FirstSolutionStop(cp_model.CpSolverSolutionCallback):
    def __init__(self, goal: int) -> None:
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.goal = goal
        self.version = "0.1"

    def on_solution_callback(self):
        if self.ObjectiveValue() >= self.goal:
            self.StopSearch()  # Stop after the first solution
        # logging.info(
        #     f"Anzahl Kanten bei dieser Lösung: {self.ObjectiveValue()}")


class Ortools(Solver):
    NAME = "Ortools"

    def __init__(self, graph: Graph_Wrapper) -> None:
        super().__init__(graph)
        self.name = self.NAME
        self.model = cp_model.CpModel()
        self.aktive_constrinsts = ""

    def constraint_intersection(self):
        if self.graph is None:
            raise ValueError("Graph is not set. Please set the graph before solving.")
        self.aktive_constrinsts += "intersection, "
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
            self.model.AddBoolOr([self.vars[edge].Not(), self.vars[other_edge].Not()])
        self.timeout_error()

    def constraint_degree(self):
        self.aktive_constrinsts += "degree, "
        if self.graph is None:
            raise ValueError("Graph is not set. Please set the graph before solving.")
        for node in self.graph.get_all_nodes():
            degree = self.graph._data.nodes[node]["degree"]
            summ = 0
            for edge in self.graph._data.edges(node):
                if edge in self.vars:
                    summ += self.vars[edge]
                else:
                    summ += self.vars[(edge[1], edge[0])]
            self.model.Add(summ == degree)

    def constraint_set_number_edges(self, number_edges: int):
        self.aktive_constrinsts += "set_edges(int), "
        if self.graph is None:
            raise ValueError("Graph is not set. Please set the graph before solving.")
        if number_edges < 0:
            raise ValueError("Number of edges must be non-negative.")
        summ = sum(self.vars.values())
        self.model.Add(summ == number_edges)

    def evaluation_direction(self):
        self.aktive_constrinsts += "eval_direction, "
        evaluation = 0.0
        nodes = self.graph.get_all_nodes()
        for node in nodes:
            desired_degree = self.graph.get_desired_degree_node(node)
            degree = sum(
                self.vars[(min(edge[0], edge[1]), max(edge[0], edge[1]))]
                for edge in self.graph.get_edges_of_node(node)
            )
            max_degree = self.graph.get_max_degree
            diff = self.model.NewIntVar(-max_degree, max_degree, "diff")
            self.model.Add(diff == degree - desired_degree)

            abs_diff = self.model.NewIntVar(0, max_degree, "abs_diff")
            self.model.AddAbsEquality(abs_diff, diff)
            min_var = self.model.NewIntVar(0, max_degree, "min_var")
            self.model.AddMinEquality(min_var, [abs_diff, desired_degree])
            x = desired_degree - min_var
            assert x is not None, "Evaluation value cannot be None"
            evaluation += x
        self.model.Maximize(evaluation)

    def degree_direction(self):
        self.aktive_constrinsts += "degree_direction, "
        nodes = self.graph.get_all_nodes()
        max_degree = self.graph.get_max_degree
        self.vars_int = {
            node: self.model.NewIntVar(0, max_degree, f"degree_{node}")
            for node in nodes
        }
        for node in nodes:
            desired_degree = self.graph.get_desired_degree_node(node)
            degree = sum(
                self.vars[(min(edge[0], edge[1]), max(edge[0], edge[1]))]
                for edge in self.graph.get_edges_of_node(node)
            )
            self.model.Add(self.vars_int[node] >= degree - desired_degree)
            self.model.Add(self.vars_int[node] >= desired_degree - degree)

        self.model.Maximize(sum(self.vars_int.values()))

    def _actual_solver(self, parameter: dict) -> dict:
        if self.graph is None:
            raise ValueError("Graph is not set. Please set the graph before solving.")
        self.graph.add_all_possible_edges(default_for_active=False)
        self.vars = {
            (min(edge[0], edge[1]), max(edge[0], edge[1])): self.model.NewBoolVar(
                f"edge_{edge[0]}_{edge[1]}"
            )
            for edge in self.graph.get_all_edges()
        }

        stop_after_first_solution = True
        if parameter["version"] == 0.1:
            self.model.Maximize(sum(list(self.vars.values())))
            self.constraint_intersection()
            self.constraint_degree()
        if parameter["version"] == 0.2:
            self.constraint_intersection()
            self.constraint_degree()
            self.constraint_set_number_edges(
                self.graph.get_number_edges_in_Triangulation()
            )
        if parameter["version"] == 0.3:
            if parameter["timeout"] == -1:
                logging.warning("Es sollte ein Timeout gesetzt werden.")
            time_function(self.constraint_intersection)()
            time_function(self.evaluation_direction)()
            self.constraint_set_number_edges(
                self.graph.get_number_edges_in_Triangulation()
            )
            stop_after_first_solution = False
        else:
            if parameter["timeout"] == -1:
                logging.warning("Es sollte ein Timeout gesetzt werden.")
            time_function(self.constraint_intersection)()
            time_function(self.degree_direction)()
            self.constraint_set_number_edges(
                self.graph.get_number_edges_in_Triangulation()
            )
            stop_after_first_solution = False

        solver = cp_model.CpSolver()
        # solver.parameters.log_search_progress = True  # Enable logging
        solver.parameters.max_time_in_seconds = self.get_remaining_time()
        logging.info("Start solving...")
        if stop_after_first_solution:
            status = solver.Solve(
                self.model,
                FirstSolutionStop(self.graph.get_number_edges_in_Triangulation()),
            )
        else:
            status = time_function(solver.Solve)(self.model)
        # status = solver.Solve(self.model)
        print(status)
        if not (status == cp_model.OPTIMAL or status == cp_model.FEASIBLE):
            logging.warning("No solution found.")
            return {
                "success": False,
                "info": self.aktive_constrinsts,
            }
        for edge, var in zip(self.graph.get_all_edges(), self.vars.values()):
            if solver.BooleanValue(var):
                self.graph.activate_edge(edge)
        return {
            "success": True,
            "info": self.aktive_constrinsts,
        }

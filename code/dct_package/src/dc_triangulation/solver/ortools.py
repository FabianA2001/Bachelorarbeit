import time
from dataclasses import dataclass

from ortools.sat.python import cp_model

from ..graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from ..utils import time_function
from .solver import Solver


@dataclass
class Parameter:
    intersection: bool = False
    all_edges: bool = False
    degree: bool = False
    fix_hull: bool = False
    number_edges: bool = False
    evaluation_direction: bool = False
    save_state_after_solution: bool = False
    min_max_direction: bool = False
    maximize_edges: bool = False
    exclude_edges: bool = False
    fix_edges: bool = False
    run_num: int = 0


class FirstSolutionStop(cp_model.CpSolverSolutionCallback):
    def __init__(self, goal: int) -> None:
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.goal = goal
        self.version = "0.1"

    def on_solution_callback(self):
        if self.ObjectiveValue() >= self.goal:
            self.StopSearch()  # Stop after the first solution
        # self.logger.info(
        #     f"Anzahl Kanten bei dieser Lösung: {self.ObjectiveValue()}")


class Save_State_Of_Solution(cp_model.CpSolverSolutionCallback):
    def __init__(self, vars_dict) -> None:
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.stats = []
        self.vars_dict = vars_dict

    def on_solution_callback(self):
        # Sammle die aktiven Kanten für diese Lösung
        active_edges = []
        for edge, var in self.vars_dict.items():
            if self.BooleanValue(var):
                active_edges.append(edge)

        state = {}
        state["timestamp"] = time.time()
        state["active_edges"] = active_edges
        state["objective_value"] = self.ObjectiveValue()
        state["best_objective_bound"] = self.best_objective_bound
        self.stats.append(state)


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
        all_intersections = time_function(self.graph.get_all_intersections_cpp)(
            self.timeout_error
        )
        for edge, intersections in all_intersections.items():
            for intersection in intersections:
                self.model.add_at_most_one(self.vars[edge], self.vars[intersection])
        self.timeout_error()

    def constraint_all_edges(self):
        intersection_all = self.graph.get_all_intersections_cpp(self.timeout_error)
        for edge, intersections in intersection_all.items():
            self.model.add(
                sum(self.vars[intersection] for intersection in intersections)
                + self.vars[edge]
                >= 1
            )

    def constraint_degree(self):
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

    def constraint_set_hull_fix(self):
        hull = self.graph.get_hull_edges()
        for edge in hull:
            self.model.Add(self.vars[edge] == 1)

    def constraint_exclude_edges(self):
        for edge in self.graph.exclude_edges:
            self.model.Add(self.vars[edge] == 0)

    def constraint_set_number_edges(self, number_edges: int):
        if self.graph is None:
            raise ValueError("Graph is not set. Please set the graph before solving.")
        if number_edges < 0:
            raise ValueError("Number of edges must be non-negative.")
        summ = sum(self.vars.values())
        self.model.Add(summ == number_edges)

    def evaluation_direction(self):
        evaluation = 0.0
        nodes = self.graph.get_all_nodes()
        for node in nodes:
            desired_degree = self.graph.get_desired_degree_node(node)
            degree = sum(
                self.vars[(min(edge[0], edge[1]), max(edge[0], edge[1]))]
                for edge in self.graph.get_edges_of_node(node)
            )
            max_degree = self.graph.get_max_degree
            abs_diff = self.model.NewIntVar(0, max_degree, "abs_diff")
            self.model.AddAbsEquality(abs_diff, degree - desired_degree)
            min_var = self.model.NewIntVar(0, max_degree, "min_var")
            self.model.AddMinEquality(min_var, [abs_diff, desired_degree])
            x = desired_degree - min_var
            assert x is not None, "Evaluation value cannot be None"
            evaluation += x
        self.model.Maximize(evaluation)

    def evaluation_max_min(self):
        nodes = self.graph.get_all_nodes()
        var_max_min = self.model.NewIntVar(0, len(nodes), "max_min")
        self.model.Add(var_max_min >= 0)
        for node in nodes:
            desired_degree = self.graph.get_desired_degree_node(node)
            degree = sum(
                self.vars[(min(edge[0], edge[1]), max(edge[0], edge[1]))]
                for edge in self.graph.get_edges_of_node(node)
            )
            max_degree = self.graph.get_max_degree
            abs_diff = self.model.NewIntVar(0, max_degree, "abs_diff")
            self.model.AddAbsEquality(abs_diff, degree - desired_degree)
            self.model.Add(abs_diff <= var_max_min)
        self.model.Minimize(var_max_min)

    def fix_edges_constraint(self):
        for edge in self.graph.fix_edges:
            if edge not in self.vars:
                raise ValueError(f"Edge {edge} not found in vars.")
            index = self.vars[edge]
            # Setze die Kante als aktiv
            self.model.Add(index == 1)

        self.timeout_error()

    def pre_solve(
        self, parameter_data: Parameter, timeout: int, parameter: dict
    ) -> bool:
        self.graph.add_all_possible_edges(default_for_active=False)
        self.vars = {
            (min(edge[0], edge[1]), max(edge[0], edge[1])): self.model.NewBoolVar(
                f"edge_{edge[0]}_{edge[1]}"
            )
            for edge in self.graph.get_all_edges()
        }

        # Apply constraints based on parameter_data
        if parameter_data.maximize_edges != False:
            assert isinstance(parameter_data.maximize_edges, (float, int)), (
                "maximize_edges must be a float or int."
            )
            for edge in parameter.get("debug_set_edges", []):
                if edge not in self.vars:
                    raise ValueError(f"Edge {edge} not found in vars.")
                self.model.Add(self.vars[edge] == 1)

            for edge in parameter.get("debug_exclude_edges", []):
                if edge not in self.vars:
                    raise ValueError(f"Edge {edge} not found in vars.")
                self.model.Add(self.vars[edge] == 0)

        if parameter_data.intersection:
            self.add_time(self.constraint_intersection)()

        if parameter_data.all_edges:
            self.add_time(self.constraint_all_edges)()

        if parameter_data.degree:
            self.add_time(self.constraint_degree)()

        if parameter_data.fix_hull:
            self.add_time(self.constraint_set_hull_fix)()

        if parameter_data.exclude_edges:
            self.add_time(self.constraint_exclude_edges)()

        if parameter_data.number_edges:
            self.add_time(self.constraint_set_number_edges)(
                self.graph.get_number_edges_in_Triangulation()
            )
        if parameter_data.fix_edges:
            self.add_time(self.fix_edges_constraint)()

        stop_after_first_solution = True
        if parameter_data.evaluation_direction:
            if timeout == -1:
                self.logger.warning("Es sollte ein Timeout gesetzt werden.")
            self.add_time(self.evaluation_direction)()
            stop_after_first_solution = False

        if parameter_data.min_max_direction:
            if timeout == -1:
                self.logger.warning("Es sollte ein Timeout gesetzt werden.")
            self.add_time(self.evaluation_max_min)()
            stop_after_first_solution = False

        return stop_after_first_solution

    def _actual_solver(self, parameter: dict) -> dict:
        if not isinstance(parameter, dict):
            raise TypeError("Parameter must be a dictionary.")

        args = parameter.get("args", None)
        assert args is not None, "Args must be provided in the parameter dictionary."
        parameter_data: Parameter = Parameter(**(args))

        # HACK
        if isinstance(parameter_data.maximize_edges, bool):
            if parameter_data.maximize_edges:
                raise ValueError(
                    "Wird als hack mit float in eval6 genutzt, super dumm aber die var wird glaube nicht mehr genutzt und so ist es am einfachsten"
                )

        if self.graph is None:
            raise ValueError("Graph is not set. Please set the graph before solving.")
        stop_after_first_solution = self.time_pre_solve(self.pre_solve)(
            parameter_data, parameter["timeout"], parameter
        )
        solver = cp_model.CpSolver()
        # solver.parameters.log_search_progress = True  # Enable logging
        solver.parameters.max_time_in_seconds = self.get_remaining_time()
        self.logger.info("Start solving...")

        stats = []
        start_solve = time.time()
        if stop_after_first_solution:
            assert parameter_data.save_state_after_solution is False, (
                "Stop after first solution"
            )
            status = self.time_solver(solver.Solve)(
                self.model,
                FirstSolutionStop(self.graph.get_number_edges_in_Triangulation()),
            )
        else:
            if parameter_data.save_state_after_solution:
                save_state_callback = Save_State_Of_Solution(self.vars)
                status = self.time_solver(solver.Solve)(self.model, save_state_callback)
                stats = save_state_callback.stats
            else:
                status = self.time_solver(solver.Solve)(self.model)
        # status = solver.Solve(self.model)
        self.logger.info(status)
        if not (status == cp_model.OPTIMAL or status == cp_model.FEASIBLE):
            self.logger.warning("No solution found.")
            return {"success": False, "stats": stats, "start_solve": start_solve}
        for edge, var in zip(self.graph.get_all_edges(), self.vars.values()):
            if solver.BooleanValue(var):
                self.graph.activate_edge(edge)
        return {"success": True, "stats": stats, "start_solve": start_solve}

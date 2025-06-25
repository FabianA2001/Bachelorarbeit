from dataclasses import dataclass

from ..graph_utils.graph_wrapper.graph_wrapper import Graph_Wrapper
from .solver import Solver

"""
wenn ein or im Name ist True das erste und False das zweite
sonnst aktiviert True den constrient
"""


@dataclass
class Parameter:
    intersection: bool = False


class Gurobi(Solver):
    NAME = "gurobi"

    def __init__(self, graph: Graph_Wrapper) -> None:
        super().__init__(graph)
        self.name = self.NAME

    def _actual_solver(self, parameter: dict) -> dict:
        if not isinstance(parameter, dict):
            raise TypeError("Parameter must be a dictionary.")
        args = parameter.get("args", None)
        assert args is not None, "Parameter 'args' must be provided in the dictionary."
        parameter_data: Parameter = Parameter(**(args))

        try:
            return {
                "success": False,
            }
        except TimeoutError:
            self.logger.warning(f"{self.name} timed out.")
            return {
                "success": False,
            }

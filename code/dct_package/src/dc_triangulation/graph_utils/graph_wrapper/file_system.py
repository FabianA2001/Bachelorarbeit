from .. import graph_const
from ..node import save_nodes_as_json
from .data import Data


def save_graph_as_json(
    data: Data, path: str, filename: str = graph_const.DEFAULT_FILE_NAME
) -> None:
    save_nodes_as_json(data.get_aktive_graph_nodes, path, filename)

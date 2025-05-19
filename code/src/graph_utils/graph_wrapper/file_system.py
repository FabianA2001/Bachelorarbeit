import networkx as nx
import matplotlib.pyplot as plt
from graph_utils import graph_const
from graph_utils.node import Node, save_nodes_as_json
import shapely
import itertools
from typing import Tuple, Union, Optional
import logging
import math
import random
from graph_utils.graph_wrapper.data import Data


def save_graph_as_json(
    data: Data, filename: str = graph_const.DEFAULT_FILE_NAME
) -> None:
    save_nodes_as_json(data.get_aktive_graph_nodes(), filename)

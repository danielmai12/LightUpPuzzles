from utils import *
from heuristics import *
import time
import sys

# Variables
stack = []
variables = []
heuristic_mode = ''
processed_puzzle = read_file("samples.txt")[1]


# Enums
class HeuristicMode:
    NONE = ''  # no constraint
    H1 = "H1"  # most constrained
    H2 = "H2"  # most constraining
    H3 = "H3"  # hybrid


def backtrack():
    """
    - Implement backtracking algorithm using DFS (stack-like)
    - Improvements by heuristics: None - H1 - H2 - H3
    :return: Solution
    """
    stack.append(([-1, -1], variables, 0, []))



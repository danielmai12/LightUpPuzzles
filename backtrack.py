from utils import *
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


# def place_bulb(existing_bulb, curr, placeholder, new, old):
#     puzzle = processed_puzzle
#
#     for bulb in range(len(existing_bulb)):
#         puzzle[existing_bulb[bulb][0]][existing_bulb[bulb][1]] = placeholder
#
#     puzzle[curr[0]][curr[1]] = placeholder
#
#     bulbs = list(existing_bulb)
#     bulbs.append(curr)
#
#     for bulb in range(len(bulbs)):
#         seen_wall_up =


list_of_available = [[[-1, 1], ]]










# def main(argv=None):


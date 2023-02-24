from utils import *
from heuristics import *
import sys

# Variables & Constants
stack = []
variables = []
heuristic_mode = ''
MAX_SEARCH_ITERATIONS = 100000
nodes = 0


# Enums
class HeuristicMode:
    NONE = ''  # no constraint
    H1 = "H1"  # most constrained
    H2 = "H2"  # most constraining
    H3 = "H3"  # hybrid


def initialize(puzzle):
    available_cells = []
    candidates = []

    for row in range(len(puzzle)):
        for col in range(len(puzzle[0])):
            if puzzle[row][col] == CellState.EMPTY:
                available_cells.append((row, col))
                candidates.append((row, col))

    return available_cells, candidates


def backtrack(initial_state):
    available_cells, candidates = initialize(initial_state)
    domain = (CellState.BULB, CellState.EMPTY)
    solutions = []
    has_solution = backtrack_recursive(initial_state.copy(), candidates, domain, solutions)

    if has_solution:
        print_puzzle(solutions[0])
        print("Number of nodes visited: {}".format(nodes))
    else:
        print("solution doesn't exist")


def backtrack_recursive(curr_state, candidates, domain, solutions):
    """
    - Implement backtracking algorithm using DFS
    - Improvements by heuristics: None - H1 - H2 - H3
    """
    global nodes

    if is_solved(curr_state):
        solutions.append(curr_state)
        return True

    if len(candidates) == 0:
        return False

    cell = candidates.pop(0)
    row_cell = cell[0]
    col_cell = cell[1]

    temp_candidates = candidates.copy()

    for state in domain:
        nodes += 1
        if state == CellState.BULB:
            curr_state[row_cell][col_cell] = CellState.BULB
            if is_state_valid(curr_state):
                if backtrack_recursive(curr_state, candidates, domain, solutions):
                    return True
            else:
                curr_state[row_cell][col_cell] = CellState.EMPTY
        else:
            candidates = temp_candidates
            if backtrack_recursive(curr_state, candidates, domain, solutions):
                return True

    return len(solutions) != 0


# Test functions
puz = read_file("test.txt")[0]
backtrack(puz)








from utils import *
from heuristics import *
import sys
import random
import copy
import argparse
import time

# Variables & Constants
MAX_SEARCH_ITERATIONS = 200000
nodes = 0


# Enums
class HeuristicMode:
    NONE = ''  # no constraint
    H1 = "H1"  # most constrained
    H2 = "H2"  # most constraining
    H3 = "H3"  # hybrid


def initialize(puzzle):
    candidates = []

    for row in range(len(puzzle)):
        for col in range(len(puzzle[0])):
            if puzzle[row][col] == CellState.EMPTY:
                candidates.append((row, col))

    return candidates


def backtrack(initial_state, heuristic=HeuristicMode.NONE):
    candidates = initialize(initial_state)
    domain = (CellState.BULB, CellState.EMPTY)
    solutions = []
    temp_state = initial_state.copy()
    trivial_solve(temp_state, candidates)
    backtrack_recursive(temp_state, candidates, domain, solutions, heuristic)

    if len(solutions) != 0:
        print_puzzle(solutions[0])
        print("Number of nodes visited: {}".format(nodes))
    elif nodes <= MAX_SEARCH_ITERATIONS:
        print("solution doesn't exist")
    else:
        print("Time Out!!!")


def backtrack_recursive(curr_state, candidates, domain, solutions, heuristic):
    """
    - Implement backtracking algorithm using DFS
    - Improvements by heuristics: None - H1 - H2 - H3
    @:param cur_state: 2-d puzzle board
    @:param candidates: list of empty cells
    @:param domain: BULB & EMPTY
    @:param solutions: contains the solution if exists
    @:param heuristic: NONE, H1, H2, H3
    """
    global nodes

    if is_solved(curr_state):
        solutions.append(copy.deepcopy(curr_state))
        return

    if len(candidates) == 0:
        return

    if nodes > MAX_SEARCH_ITERATIONS:
        return

    curr_most_potentials = []
    if heuristic == HeuristicMode.H1:
        curr_most_potentials = h1(curr_state, candidates)
    elif heuristic == HeuristicMode.H2:
        curr_most_potentials = h2(curr_state, candidates)
    elif heuristic == HeuristicMode.H3:
        curr_most_potentials = h3(curr_state, candidates)

    if len(curr_most_potentials) >= 1:
        next_cell = curr_most_potentials[random.randint(0, len(curr_most_potentials) - 1)]
    else:
        next_cell = candidates[0]

    candidates.remove(next_cell)
    row_cell, col_cell = next_cell[0], next_cell[1]
    temp_candidates = copy.deepcopy(candidates)
    temp_state = copy.deepcopy(curr_state)

    for state in domain:
        nodes += 1
        curr_state[row_cell][col_cell] = state
        if is_state_valid(curr_state):
            if backtrack_recursive(curr_state, candidates, domain, solutions, heuristic):
                return len(solutions) != 0
        candidates = temp_candidates
        curr_state = temp_state


def trivial_solve(curr_state, candidates):
    """ Place all the light bulbs which can be placed for sure.
        This can be done if there are exactly n neighbour of a constrained wall (n).
    """

    walls = []
    for row in range(len(curr_state)):
        for col in range(len(curr_state[row])):
            if curr_state[row][col].isdigit():
                walls.append([row, col])

    for wall_row, wall_col in walls:
        if int(curr_state[wall_row][wall_col]) == num_adjacent_neighbors(curr_state, wall_row, wall_col):
            if wall_row > 0:
                curr_state[wall_row - 1][wall_col] = CellState.BULB
                if (wall_row - 1, wall_col) in candidates: candidates.remove((wall_row - 1, wall_col))
            if wall_row < len(curr_state) - 1:
                curr_state[wall_row + 1][wall_col] = CellState.BULB
                if (wall_row + 1, wall_col) in candidates: candidates.remove((wall_row + 1, wall_col))
            if wall_col > 0:
                curr_state[wall_row][wall_col - 1] = CellState.BULB
                if (wall_row, wall_col - 1) in candidates: candidates.remove((wall_row, wall_col - 1))
            if wall_col < len(curr_state) - 1:
                curr_state[wall_row][wall_col + 1] = CellState.BULB
                if (wall_row, wall_col + 1) in candidates: candidates.remove((wall_row, wall_col + 1))


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    arg_parser = argparse.ArgumentParser(add_help=False)
    arg_parser.add_argument('-p', action='store', dest='file_name', type=str, default='test.txt')
    arg_parser.add_argument('-h', action='store', dest='heuristic', type=str, default='')

    arguments = arg_parser.parse_args(argv)
    file_name = arguments.file_name
    heuristic = arguments.heuristic
    puzzle_dict = read_file(file_name)

    for i in puzzle_dict.keys():
        starting_time = time.time()
        backtrack(puzzle_dict[i], heuristic)
        ending_time = time.time()
        print("The program was run for {} seconds.".format(ending_time - starting_time))


if __name__ == '__main__':
    main()
    

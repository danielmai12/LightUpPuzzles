from heuristics import *

import argparse
import sys
from typing import List
import random
import time
import copy

# forward checking algorithm, with corresponding heuristic
# check the status of the current "solution", or node, to see if it could be on the path to the solution,
# return False if it cannot be possibly part of a solution
def check_curr_state(puzzle, non_assigned_cells) -> bool:
    # if a cell can be a bulb or empty, its priority is 3
    for r in range(len(puzzle)):
        for c in range(len(puzzle[r])):
            value = len(puzzle) * r + c
            if value in non_assigned_cells:
                puzzle[r][c] = 3

    # if a cell cannot be a bulb, its priority is 1.
    for r in range(len(puzzle)):
        for c in range(len(puzzle[r])):
            if puzzle[r][c] == 'b':
                prioritize_bulbs(puzzle, r, c)

    # if a cell cannot be empty but can be a bulb, assign 2 as its priority,
    # priority 0 if it can't be neither
    for r in range(len(puzzle)):
        for c in range(len(puzzle[r])):
            if puzzle[r][c] in wall_values:
                num_adj_bulbs = count_adjacent_bulbs(puzzle, r, c)
                potential_bulbs = generate_potential_bulbs_to_wall(puzzle, r, c)
                cell_status = check_edge_corner(puzzle, r, c)

                require_bulbs = int(puzzle[r][c]) - num_adj_bulbs - cell_status
                if require_bulbs == potential_bulbs:
                    prioritize_walls(puzzle, r, c)

    result = True
    for r in range(len(puzzle)):
        for c in range(len(puzzle[r])):
            if isinstance(puzzle[r][c], int):
                if puzzle[r][c] == 0:
                    result = False
                puzzle[r][c] = '_'
    return result

def forward_checking(puzzle, domain, empty_cells, heuristic: str):

    global node_count
    node_count += 1

    # printing solving status

    #TODO: maybe not using this many print statements...
    '''
    if node_count < 10000:
        if node_count % 3 == 0:
            print('\rProcessing.')
        if node_count % 3 == 1:
            print('\rProcessing..')
        if node_count % 3 == 2:
            print('\rProcessing...')
    '''

    if node_count % 10000 == 0:
        print('\rAlready processed {} nodes.'.format(node_count))

    if node_count == 5000000:
        return 'Number of nodes processed is too high!! Timeout!'

    if validate_wall_condition(puzzle):
        return puzzle

    # backtrack if the current solution is at dead end
    if len(empty_cells) == 0 and check_curr_state(puzzle, empty_cells):
        return 'backtrack'

    next_potential_cells = []

    # Check input for the heuristic to use
    if heuristic == 'most_constrained':
        next_potential_cells = h1(puzzle, empty_cells)  # Find most constrained
    elif heuristic == 'most_constraining':
        next_potential_cells = h2(puzzle, empty_cells)  # Find most constraining
    elif heuristic == 'hybrid':
        next_potential_cells = h3(puzzle, empty_cells)  # Hybrid
    else:
        print('\n*** ERROR *** Heuristic must be either "most_constrained", "most_constraining" or "hybrid".')
        return 'Abort!!'

    # If we have more than 1 chosen cells, randomly pick 1
    # else, pick the only one we have
    next_cell = []
    if len(next_potential_cells) >= 1:
        next_cell = next_potential_cells[random.randint(0, len(next_potential_cells) - 1)]

    # remove the cell chosen above from the list of empty cells
    empty_cells.remove(next_cell)

    row, col = next_cell[0], next_cell[1]

    for value in domain:
        puzzle[row][col] = value
        #TODO: do we really need the first half of the if statement? If yes, modify ccan_bulb_be_here, else delete it
        if (value != CellState.EMPTY and can_bulb_be_here(puzzle, row, col)) or value == CellState.EMPTY:
            result = forward_checking(puzzle, domain, empty_cells, heuristic)
            if result != 'backtrack':
                return result

    empty_cells.append(next_cell)
    return 'backtrack'


# get all the empty cells in the map, which are potential places for bulbs.
def get_empty_cells(puzzle: List[List[str]]) -> List[List[int]]:

    """
    :param puzzle: List[List[str]]
    :return: List[List[int]], the coordinates of empty cells in the puzzle
    """

    empty_cells = []

    for row in range(len(puzzle)):
        for col in range(len(puzzle[row])):
            if puzzle[row][col] == '_':
                empty_cells.append([row, col])

    return empty_cells

# check if a given cell is inside the map
def is_inside(puzzle: List[List[str]], r: int, c: int) -> bool:
    return 0 <= r < len(puzzle) and 0 <= c < len(puzzle[0])


# given a cell, check if we can place a bulb there
def can_bulb_be_here(puzzle: List[List[str]], r: int, c: int) -> bool:
    delta_r = [-1, 1, 0, 0]
    delta_c = [0, 0, -1, 1]
    for i in range(len(delta_c)):
        moving_r = r + delta_r[i]
        moving_c = c + delta_c[i]

        if is_inside(puzzle, moving_r, moving_c) and puzzle[moving_r][moving_c] in wall_values:
            # if there is already enough number of bulbs for that well
            if count_adjacent_bulbs(puzzle, moving_r, moving_c) > int(puzzle[moving_r][moving_c]):
                return False

        while is_inside(puzzle, moving_r, moving_c) and not puzzle[moving_r][moving_c] in wall_values:
            if puzzle[moving_r][moving_c] == 'b':  # adjacent bulbs
                return False
            moving_r += delta_r[i]
            moving_c += delta_c[i]
    return True

# call necessary methods/algorithms to solve the puzzle as required.
def solve_puzzle(puzzle: List[List[str]], heuristic: str):
    domain = ('b', '_')
    non_assigned = get_empty_cells(puzzle)
    # TODO: finish pre_process()
    # pre_process(puzzle, non_assigned)
    print("Chosen heuristic: {}.".format(heuristic))
    return forward_checking(puzzle, domain, non_assigned, heuristic)


# receive input, process input and call necessary methods to solve the puzzle.
def main(argv=None):

    if argv is None:
        argv = sys.argv[1:]

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--heuristic', action='store', dest='heuristic', type=str, default='most_constrained')

    arguments = arg_parser.parse_args(argv)

    # TODO: check if read_file works the same as read_puzzle()
    puzzle = read_file()

    starting_time = time.time()
    solution = solve_puzzle(puzzle, arguments.heuristic)
    ending_time = time.time()

    if solution == 'Too many nodes. Timeout!':
        print('Too many nodes. Timeout.\nIt took {} seconds.'.format(ending_time - starting_time))

    elif solution == 'stop':
        print('Please retry!')

    else:
        print('*** Done! ***\nThe solution is printed out below:')
        print_puzzle(solution)
        print("The puzzle was solved in {} seconds.".format(ending_time - starting_time))
    print('Visited {} nodes.'.format(num_nodes))


if __name__ == '__main__':
    main()
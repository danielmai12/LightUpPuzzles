from heuristics import *

import argparse
import sys
from typing import List
import random
import time
import copy

node_count = 0
# count the number of neighbouring bulbs surrounding a cell
def count_adjacent_bulbs(puzzle: List[List[str]], r: int, c: int) -> int:
    num_bulbs = 0
    if r > 0 and puzzle[r - 1][c] == 'b':
        num_bulbs += 1
    if r < len(puzzle) - 1 and puzzle[r + 1][c] == 'b':
        num_bulbs += 1
    if c > 0 and puzzle[r][c - 1] == 'b':
        num_bulbs += 1
    if c < len(puzzle[0]) - 1 and puzzle[r][c + 1] == 'b':
        num_bulbs += 1
    return num_bulbs

def prioritize_bulbs(puzzle, r: int, c: int):
    moving_r = r - 1
    while moving_r >= 0 and isinstance(puzzle[moving_r][c], int):
        puzzle[moving_r][c] = puzzle[moving_r][c] % 2
        moving_r -= 1

    moving_r = r + 1
    while moving_r < len(puzzle) - 1 and isinstance(puzzle[moving_r][c], int):
        puzzle[moving_r][c] = puzzle[moving_r][c] % 2
        moving_r += 1

    moving_c = c - 1
    while moving_c >= 0 and isinstance(puzzle[r][moving_c], int):
        puzzle[r][moving_c] = puzzle[r][moving_c] % 2
        moving_c -= 1

    moving_c = c + 1
    while moving_c < len(puzzle[r]) - 1 and isinstance(puzzle[r][moving_c], int):
        puzzle[r][moving_c] = puzzle[r][moving_c] % 2
        moving_c += 1


def prioritize_walls(puzzle, r, c):
    moving_r = r - 1
    if r > 0 and isinstance(puzzle[moving_r][c], int):
        puzzle[moving_r][c] = int(puzzle[moving_r][c] / 2) * 2
        if puzzle[moving_r][c] == 2:
            prioritize_bulbs(puzzle, moving_r, c)

    moving_r = r + 1
    if r < len(puzzle) - 1 and isinstance(puzzle[moving_r][c], int):
        puzzle[moving_r][c] = int(puzzle[moving_r][c] / 2) * 2
        if puzzle[moving_r][c] == 2:
            prioritize_bulbs(puzzle, moving_r, c)

    moving_c = c - 1
    if c > 0 and isinstance(puzzle[r][moving_c], int):
        puzzle[r][moving_c] = int(puzzle[r][moving_c] / 2) * 2
        if puzzle[r][moving_c] == 2:
            prioritize_bulbs(puzzle, r, moving_c)

    moving_c = c + 1
    if c < len(puzzle[0]) - 1 and isinstance(puzzle[r][moving_c], int):
        puzzle[r][moving_c] = int(puzzle[r][moving_c] / 2) * 2
        if puzzle[r][moving_c] == 2:
            prioritize_bulbs(puzzle, r, moving_c)


# check to see among all adjacent cells, how many are potential places for bulbs,
# >=2 as empty with priority 2 can be bulbs
def generate_potential_bulbs_to_wall(curr_state, row, col):
    """
    # The cell input in this method are only wall cell (cell with number)
    # check to see among all adjacent cells of this cell, how many are potential places are there for bulbs,
    # >=2 as empty with priority 2 can be bulbs

    :param curr_state: List[List[str]] - the current state of the puzzle
    :param row: int - row index of the given cell
    :param col: int - col index of the given cell
    :return: int
    """

    num_bulbs = 0

    # check all for neighbours
    if row > 0 and isinstance(curr_state[row - 1][col], int) and curr_state[row - 1][col] >= 2:
        num_bulbs += 1
    if row < len(curr_state) - 1 and isinstance(curr_state[row + 1][col], int) and curr_state[row + 1][col] >= 2:
        num_bulbs += 1
    if col > 0 and isinstance(curr_state[row][col - 1], int) and curr_state[row][col - 1] >= 2:
        num_bulbs += 1
    if col < len(curr_state[0]) - 1 and isinstance(curr_state[row][col + 1], int) and curr_state[row][col + 1] >= 2:
        num_bulbs += 1
    return num_bulbs

# forward checking algorithm
# check the status of the current "solution", or node, to see if it could be on the path to the solution,
# return False if it cannot be possibly part of a solution

def check_curr_sol_for_feasibility(curr_state, non_assigned_cells) -> bool:

    # if a cell can be a bulb or empty, its priority is 3
    for row in range(len(curr_state)):
        for col in range(len(curr_state[row])):
            value = len(curr_state) * row + col
            if value in non_assigned_cells:
                curr_state[row][col] = 3

    # if a cell cannot be a bulb, its priority is 1.
    for row in range(len(curr_state)):
        for col in range(len(curr_state[row])):
            if curr_state[row][col] == 'b':
                prioritize_bulbs(curr_state, row, col)

    # Check each wall with number
    # if a cell cannot be empty but can be a bulb, assign 2 as its priority,
    # priority 0 if it can't be neither
    for row in range(len(curr_state)):
        for col in range(len(curr_state[row])):
            if curr_state[row][col].isdigit():

                # The number at this wall
                wallNum = int(curr_state[row][col])

                # Number of bulbs that are adjacent to this wall
                num_adj_bulbs = num_adjacent_lights(curr_state, row, col)

                # Number of potential bulbs that are adjacent to the wall
                potential_bulbs = generate_potential_bulbs_to_wall(curr_state, row, col)

                # If cell is NOT at edge or corner, its status is 0
                # If at edge, status is 1
                # If at corner, status is 2
                cell_status = edge_corner_constraints(curr_state, row, col)

                require_bulbs_for_this_cell = wallNum - num_adj_bulbs - cell_status

                if require_bulbs_for_this_cell == potential_bulbs:
                    prioritize_walls(curr_state, row, col)

    result = True

    # Iterating the entire puzzle and set the puzzle to normal ????
    for row in range(len(curr_state)):
        for col in range(len(curr_state[row])):
            if isinstance(curr_state[row][col], int):
            #if curr_state[row][col].isdigit():
                if curr_state[row][col] == 0:
                    result = False
                curr_state[row][col] = '_'

    return result

def forward_checking(puzzle, domain, empty_cells, heuristic):

    """
    :param puzzle: List[List[str]]
    :param domain: List[str] - The domain of posible values each cell in empty cell could take
    :param empty_cells: List[List[int] - List of coordinate [x,y] of each empty cell.
    :param heuristic: String - "most_constrained", "most_constraining", or "hybrid". To decide the heuristic
    :return: The complete solution, or no solution if puzzle is not solvable
    """

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

    if node_count == 500000:
        return 'Number of nodes processed is too high!! Timeout!'

    if is_solved(puzzle):
        return puzzle

    # backtrack if the current solution is at dead end
    if len(empty_cells) == 0 and check_curr_sol_for_feasibility(puzzle, empty_cells):
        return 'backtrack'

    next_potential_cells = []

    # Check input for the heuristic to use
    if heuristic == 'h1':
        next_potential_cells = h1(puzzle, empty_cells)  # Find most constrained
    elif heuristic == 'h2':
        next_potential_cells = h2(puzzle, empty_cells)  # Find most constraining
    elif heuristic == 'h3':
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

        # If we place a bulb down, and the placement is valid
        # or if we choose not to place bulb
        # we can keep solving (recursive call)
        if value == CellState.EMPTY or ( value == CellState.BULB and is_valid_bulb(puzzle, row, col) ):
            result = forward_checking(puzzle, domain, empty_cells, heuristic)
            if result != 'backtrack':
                return result

    # At this point, the deeper recursion has failed for all values in the domain
    # so we append the empty cell we just chose, then backtrack
    # TODO: shouldn't the puzzle be rocovered to its original state b4 the loop?
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

# call necessary methods/algorithms to solve the puzzle as required.
def solve_puzzle(puzzle, heuristic):
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
    arg_parser.add_argument('--heuristic', action='store', dest='heuristic', type=str, default='h3')

    arguments = arg_parser.parse_args(argv)

    # TODO: check if read_file works the same as read_puzzle()
    puzzle = read_file("test.txt").get(0)
    print_puzzle(puzzle)

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
    print('Visited {} nodes.'.format(node_count))


if __name__ == '__main__':
    main()
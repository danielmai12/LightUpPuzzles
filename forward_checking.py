from heuristics import *

import argparse
import sys
from typing import List
import random
import time
import copy

node_count = 0

def prioritize_bulbs(puzzle, r: int, c: int):
    moving_r = r - 1
    while moving_r >= 0 and puzzle[moving_r][c].isdigit():
        puzzle[moving_r][c] = str( int(puzzle[moving_r][c]) % 2 )
        moving_r -= 1

    moving_r = r + 1
    while moving_r < len(puzzle) - 1 and puzzle[moving_r][c].isdigit():
        puzzle[moving_r][c] = str( int(puzzle[moving_r][c]) % 2 )
        moving_r += 1

    moving_c = c - 1
    while moving_c >= 0 and puzzle[r][moving_c].isdigit():
        puzzle[r][moving_c] = str( int(puzzle[r][moving_c]) % 2 )
        moving_c -= 1

    moving_c = c + 1
    while moving_c < len(puzzle[r]) - 1 and puzzle[r][moving_c].isdigit():
        puzzle[r][moving_c] = str( int(puzzle[r][moving_c]) % 2 )
        moving_c += 1


def prioritize_walls(puzzle, r, c):
    moving_r = r - 1
    if r > 0 and puzzle[moving_r][c].isdigit():
        puzzle[moving_r][c] = str( int(int(puzzle[moving_r][c]) / 2) * 2 )
        if int(puzzle[moving_r][c]) == 2:
            prioritize_bulbs(puzzle, moving_r, c)

    moving_r = r + 1
    if r < len(puzzle) - 1 and puzzle[moving_r][c].isdigit():
        puzzle[moving_r][c] = str( int(int(puzzle[moving_r][c]) / 2) * 2 )
        if int(puzzle[moving_r][c]) == 2:
            prioritize_bulbs(puzzle, moving_r, c)

    moving_c = c - 1
    if c > 0 and puzzle[r][moving_c].isdigit():
        puzzle[r][moving_c] = str( int(int(puzzle[r][moving_c]) / 2) * 2 )
        if int(puzzle[r][moving_c]) == 2:
            prioritize_bulbs(puzzle, r, moving_c)

    moving_c = c + 1
    if c < len(puzzle[0]) - 1 and puzzle[r][moving_c].isdigit():
        puzzle[r][moving_c] = str( int(int(puzzle[r][moving_c]) / 2) * 2 )
        if int(puzzle[r][moving_c]) == 2:
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
    if row > 0 and curr_state[row - 1][col].isdigit() and int(curr_state[row - 1][col]) >= 2:
        num_bulbs += 1
    if row < len(curr_state) - 1 and curr_state[row + 1][col].isdigit() and int(curr_state[row + 1][col]) >= 2:
        num_bulbs += 1
    if col > 0 and (curr_state[row][col - 1].isdigit()) and int(curr_state[row][col - 1]) >= 2:
        num_bulbs += 1
    if col < len(curr_state[0]) - 1 and curr_state[row][col + 1].isdigit() and int(curr_state[row][col + 1]) >= 2:
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
            #if isinstance(curr_state[row][col], int):
            if curr_state[row][col].isdigit():
                if int(curr_state[row][col]) == 0:
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

    if node_count == 270000:
        return 'Too many nodes. Timeout!'

    if is_solved(puzzle):
        return puzzle

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
        return 'Abort!!' \

    # If we have more than 1 chosen cells, randomly pick 1
    # else, pick the only one we have
    next_cell = []
    if len(next_potential_cells) >= 1:
        next_cell = next_potential_cells[random.randint(0, len(next_potential_cells) - 1)]
    else:    # We have no empty cell to consider, and the puzzle is still not solved, so backtrack here!
        #print("backtrack as we have no empty cell to work with")
        return 'backtrack'

    # remove the cell chosen above from the list of temporary empty cells
    temp_empty_cells = copy.deepcopy(empty_cells)
    temp_empty_cells.remove(next_cell)

    # TODO: clean this
    '''
    print()
    print('next cell is')
    print(next_cell)
    print('temp empty cell is')
    print(temp_empty_cells)
    '''

    row, col = next_cell[0], next_cell[1]

    # Get the domain of the cell we chose
    this_var_domain = domain[row][col]

    # Try each value in the domain of the chosen variable
    #for value in this_var_domain:
    for i in range(len(this_var_domain)):

        value = this_var_domain[i];

        # TODO: clean this
        #print('value for cell {} {} is {}'.format(row, col, value))

        # Create a copy of the current puzzle state for variable assignment
        temp_puzzle = copy.deepcopy(puzzle)

        temp_puzzle[row][col] = value

        # TODO: clean this
        #print("puzzle after changing the cell")
        #print_puzzle(temp_puzzle)

        temp_domain = copy.deepcopy(domain)

        domain_change(temp_domain, row, col, value)

        #TODO: clean this
        '''
        print('domain before change')
        print_domain(domain)
        print("domain after changing the cell")
        print_domain(temp_domain)
        '''

        no_empty_domain = check_no_empty_domain( temp_domain, temp_empty_cells )

        if is_state_valid(temp_puzzle) and no_empty_domain:
            result = forward_checking(temp_puzzle, temp_domain, temp_empty_cells, heuristic)
            if result != 'backtrack' and result != 'failure':
                return result

    return 'failure'

def is_domain_of_empty_cell(domain, row, col):

    """
    Return true if the domain is not the domain of a wall
    :param domain: List[List[List[String]]] - The domain of each cell. Domain values are "wall", "_" or "b
    :param row: int - row index of the given
    :param col: int - col index of the given
    :return:
    """

    result = False

    if len(domain[row][col]) > 1:
        result = True
    elif len(domain[row][col]) == 1 and domain[row][col][0] != 'wall':
        result = True
    elif len(domain[row][col]) == 0:
        result = True

    return result

def domain_change(domain, row, col, value):
    """
    # With the row-col coordinate of a chosen cell and the new value of that cell, if the new value is 'b'
    # then modifying all the '_' cell that the chosen cell could "see" by excluding "b" out of their domain
    # If the new value is '_', nothing to do
    :param domain: List[List[List[String]]] - The domain of each cell. Domain values are "wall", "_" or "b"
    :param row: int - row index of the cell that got assigned variable
    :param col: int - col index of the cell that got assigned variable
    :param value: the value of the variable (either'_' or 'b'
    :return: List[List[List[String] - the domain that is modified
    """

    #TODO: remove this after finish
    '''
    print('in domain change function, the domain passed in is:')
    print_domain(domain)
    '''

    if value == CellState.BULB:

        travel_dist = 1

        # Keep travel if we still in domain map, and the cell domain we are looking at is not wall

        # Up
        while row - travel_dist >= 0 and is_domain_of_empty_cell(domain, row - travel_dist, col):
            # We only remove if the domain has size 2, or only has bulb left
            if len(domain[row - travel_dist][col]) == 2:
                domain[row - travel_dist][col].remove('b')
            elif len(domain[row - travel_dist][col]) == 1 and domain[row - travel_dist][col][0] == CellState.BULB:
                domain[row - travel_dist][col].remove('b')
            travel_dist += 1

        travel_dist = 1

        # Down
        while row + travel_dist < len(domain) and is_domain_of_empty_cell(domain, row + travel_dist, col):
            if len(domain[row + travel_dist][col]) == 2:
                domain[row + travel_dist][col].remove('b')
            elif len(domain[row + travel_dist][col]) == 1 and domain[row + travel_dist][col][0] == CellState.BULB:
                domain[row + travel_dist][col].remove('b')
            travel_dist += 1

        travel_dist = 1

        # To the left
        while col - travel_dist >= 0 and is_domain_of_empty_cell(domain, row, col - travel_dist):
            if len(domain[row][col - travel_dist]) == 2:
                domain[row][col - travel_dist].remove('b')
            elif len(domain[row][col - travel_dist]) == 1 and domain[row][col - travel_dist][0] == CellState.BULB:
                domain[row][col - travel_dist].remove('b')
            travel_dist += 1

        travel_dist = 1

        # To the right
        while col + travel_dist < len(domain[0]) and is_domain_of_empty_cell(domain, row, col + travel_dist):
            if len(domain[row][col + travel_dist]) == 2:
                domain[row][col + travel_dist].remove('b')
            elif len(domain[row][col + travel_dist]) == 1 and domain[row][col + travel_dist][0] == CellState.BULB:
                domain[row][col + travel_dist].remove('b')
            travel_dist += 1

def check_no_empty_domain( domain, empty_cells ):

    """
    # Check domain of each empty cell
    # Return false if any empty cell has domain of len 0
    :param domain: List[List[List[String]]] - The domain of each cell. Domain values are "wall", "_" or "b"
    :param empty_cells: List[List[int]] - The coordinate of each empty cell
    :return: bool
    """

    #TODO: remove this at the end
    '''
    print('in bool function, the empty cell passed in is:')
    print(empty_cells)
    print('in bool function, the domain passed in is:')
    '''

    for cell in empty_cells:
        if len( domain[cell[0]][cell[1]] ) == 0:
            return False

    return True

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

def print_domain(domain):

    for row in range(len(domain)):
        for col in range(len(domain[row])):
            str = ''
            if len(domain[row][col]) > 1:
                str = domain[row][col][0] + '/' + domain[row][col][1]
            else:
                str = domain[row][col][0]
            if col == len(domain[0]) - 1:
                print(str)
            else:
                print(str, end='     ')

def make_empty_cell_domain(puzzle):
    """
    # If a cell is a wall, its domain is ['wall'] and will never be modified
    # If a domain is an empty cell ('_'), its domain could be ['_'], ['b'] or ['_','b']
    # domain[r][c] is the domain of the cell at row r and col c
    :param puzzle: List[List[str]] - the given puzzle
    :return: List[List[List[str]] - the domain values of each cell
    """
    row_num = range(len(puzzle))
    col_num = range(len(puzzle[0]))
    domain_of_empty_cell = [[[] for row in row_num] for col in col_num]

    for row in range(len(puzzle)):
        for col in range(len(puzzle[row])):
            if puzzle[row][col].isdigit():
                domain_of_empty_cell[row][col].append('wall')
            else:
                domain_of_empty_cell[row][col].append('b')
                domain_of_empty_cell[row][col].append('_')


    return domain_of_empty_cell


# call necessary methods/algorithms to solve the puzzle as required.
def solve_puzzle(puzzle, heuristic):

    empty_cell = get_empty_cells(puzzle)

    #TODO: clean this

    '''
    print('Initial empty cell')
    print(empty_cell)
    print('Initial domain')
    '''

    # We want to pre-process the numbers at edge and corner, then place possible bulbs
    # Then generate corresponding domain and puzzle from the pre-process puzzle
    # pre_process(puzzle, non_assigned)
    domain_of_empty_cell = make_empty_cell_domain(puzzle)
    # print_domain(domain_of_empty_cell)
    # TODO: finish pre_process()

    print("Chosen heuristic: {}.".format(heuristic))
    return forward_checking(puzzle, domain_of_empty_cell, empty_cell, heuristic)


# receive input, process input and call necessary methods to solve the puzzle.
def main(argv=None):

    if argv is None:
        argv = sys.argv[1:]

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--heuristic', action='store', dest='heuristic', type=str, default='h1')

    arguments = arg_parser.parse_args(argv)

    puzzle = read_file("test.txt").get(0)

    print('The puzzle is')
    print_puzzle(puzzle)

    starting_time = time.time()
    solution = solve_puzzle(puzzle, arguments.heuristic)
    ending_time = time.time()

    if solution == 'Too many nodes. Timeout!':
        print('Number of nodes processed is too high!! Timeout!\nIt took {} seconds.'.format(ending_time - starting_time))

    elif solution == 'stop':
        print('Please retry!')
    elif solution == 'failure':
        print('Fail to solve this puzzle. Seems like it\'s unsolvable!!')

    else:
        print('*** Done! ***\nThe solution is printed out below:')
        print_puzzle(solution)
        print("The puzzle was solved in {} seconds.".format(ending_time - starting_time))
    print('Visited {} nodes.'.format(node_count))


if __name__ == '__main__':
    main()
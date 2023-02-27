from heuristics import *
import numpy as np

import argparse
import sys
import random
import time
import copy

node_count = 0


def forward_checking(puzzle, domain, empty_cells, wall_cells, heuristic):

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

    if node_count % 10000 == 0:
        print('\rAlready processed {} nodes.'.format(node_count))

    if node_count == 500000:
        return 'Too many nodes. Timeout!'

    if is_solved(puzzle):
        return puzzle

    next_potential_cells = []

    # Check input for the heuristic to use
    if heuristic == 'H1':
        next_potential_cells = h1(puzzle, empty_cells)  # Find most constrained
    elif heuristic == 'H2':
        next_potential_cells = h2(puzzle, empty_cells)  # Find most constraining
    elif heuristic == 'H3':
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

        return 'backtrack'

    # remove the cell chosen above from the list of temporary empty cells
    temp_empty_cells = copy.deepcopy(empty_cells)
    temp_empty_cells.remove(next_cell)

    row, col = next_cell[0], next_cell[1]

    # Get the domain of the cell we chose
    this_var_domain = domain[row][col]

    # Try each value in the domain of the chosen variable
    for i in range(len(this_var_domain)):
        value = this_var_domain[i]

        # Create a copy of the current puzzle state for variable assignment
        temp_puzzle = copy.deepcopy(puzzle)

        temp_puzzle[row][col] = value

        temp_domain = copy.deepcopy(domain)

        domain_change(temp_domain, row, col, value)

        no_empty_domain = check_no_empty_domain(temp_domain, temp_empty_cells)
        feasible_for_all_wall = check_wall_feasibility(temp_puzzle, temp_domain, wall_cells)

        if is_state_valid(temp_puzzle) and no_empty_domain and feasible_for_all_wall:
            result = forward_checking(temp_puzzle, temp_domain, temp_empty_cells, wall_cells, heuristic)
            if result != 'backtrack' and result != 'failure':
                return result

    return 'failure'


def check_wall_feasibility(puzzle, domain, wall_cells):
    """
    # Check the surrounding of each wall
    # Return true if for each wall, the number of cells around it that could accept a bulb is more than or equal
    # to wall value
    :param puzzle: List[List[str]]
    :param domain: List[List[List[String]]] - The domain of each cell. Domain values are "wall", "_" or "b
    :param wall_cells: List[List[int]] - the coordinates of the walls
    :return: bool
    """

    for cell in wall_cells:

        row = cell[0]
        col = cell[1]

        wall_value = int(puzzle[row][col])
        count = 0

        if row - 1 >= 0 and CellState.BULB in domain[row - 1][col]:
            count += 1

        if row + 1 < len(domain) and CellState.BULB in domain[row + 1][col]:
            count += 1

        if col - 1 >= 0 and CellState.BULB in domain[row][col - 1]:
            count += 1

        if col + 1 < len(domain[0]) and CellState.BULB in domain[row][col + 1]:
            count += 1

        return count >= wall_value


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


def get_empty_cells(puzzle):

    """
    Take the puzzle and return the coordinates of empty cells
    :param puzzle: List[List[str]] - The puzzle
    :return: List[List[int]], the coordinates of empty cells in the puzzle
    """

    empty_cells = []

    for row in range(len(puzzle)):
        for col in range(len(puzzle[row])):
            if puzzle[row][col] == '_':
                empty_cells.append([row, col])

    return empty_cells


def get_wall_cells(puzzle):

    """
    Take the puzzle and return the coordinates of empty cells
    :param puzzle: List[List[str]] - The puzzle
    :return: List[List[int]], the coordinates of puzzle cells in the puzzle
    """

    wall_cells = []

    for row in range(len(puzzle)):
        for col in range(len(puzzle[row])):
            if puzzle[row][col].isdigit():
                wall_cells.append([row, col])

    return wall_cells


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


def take_bulb_from_cell_domain(domain, row, col):
    """
    Take bulb from the domain of a given empty cell
    Only give row and col coordinate of empty cell to this method
    :param domain: List[List[List[str]]] - The value domain of each cell in the puzzle
    :param row: int - the row coordinate of an empty cell
    :param col: int - the col coordinate of an empty cell
    :return:
    """

    if CellState.BULB in domain[row][col]:
        domain[row][col].remove(CellState.BULB)


def place_bulb_around_wall_4(puzzle, row, col, domain_of_empty_cell, empty_cells):
    """
    # Place 4 bulbs around a wall with number 4
    # The given wall is ensured to be not on the edge of the map
    # While placing bulb, check if all domain size of empty cell is still > 0,
    # there is no conflict in constraint (e.i. an empty cell that only have value domain '_' yet must be placed a bulb on"
    # and the state of the puzzle is still valid (no 2 bulbs seeing each other)
    # Return true if everything is satisfied
    :param puzzle:
    :param row:
    :param col:
    :param domain_of_empty_cell:
    :param empty_cell:
    :return:
    """

    validPuzzle= True

    if validPuzzle and CellState.BULB in domain_of_empty_cell[row-1][col]:
        puzzle[row-1][col] = CellState.BULB

        if [row - 1, col] in empty_cells:
            empty_cells.remove([row-1, col])

        domain_change(domain_of_empty_cell, row-1, col, CellState.BULB)
        validPuzzle = is_state_valid(puzzle) and check_no_empty_domain( domain_of_empty_cell, empty_cells )
    else:
        validPuzzle = False

    if validPuzzle and CellState.BULB in domain_of_empty_cell[row+1][col]:
        puzzle[row+1][col] = CellState.BULB

        if [row + 1, col] in empty_cells:
            empty_cells.remove([row+1, col])

        domain_change(domain_of_empty_cell, row+1, col, CellState.BULB)
        validPuzzle = is_state_valid(puzzle) and check_no_empty_domain( domain_of_empty_cell, empty_cells )
    else:
        validPuzzle = False

    if validPuzzle and CellState.BULB in domain_of_empty_cell[row][col-1]:
        puzzle[row][col-1] = CellState.BULB

        if [row, col-1] in empty_cells:
            empty_cells.remove([row, col-1])

        domain_change(domain_of_empty_cell, row, col-1, CellState.BULB)
        validPuzzle = is_state_valid(puzzle) and check_no_empty_domain( domain_of_empty_cell, empty_cells )
    else:
        validPuzzle = False

    if validPuzzle and CellState.BULB in domain_of_empty_cell[row][col+1]:
        puzzle[row][col+1] = CellState.BULB

        if [row, col+1] in empty_cells:
            empty_cells.remove([row, col+1])

        domain_change(domain_of_empty_cell, row, col+1, CellState.BULB)
        validPuzzle = is_state_valid(puzzle) and check_no_empty_domain( domain_of_empty_cell, empty_cells )
    else:
        validPuzzle = False

    return validPuzzle


def wall_of_3_has_exactly_3_spots(domain, row, col):

    """
    # Given a wall of number 3, count if this wall has exactly 3 available cells around it to place bulb
    # Wall are not counted, and empty cells that doesn't have bulb in its domain are not counted

    :param domain: List[List[List[str]]] - the domain of each cell in the puzzle
    :param row: int - row coordinate of a wall with value 3
    :param col: int - col coordinate of a wall with value 3
    :return: bool
    """

    count = 0

    if row-1 >= 0 and CellState.BULB in domain[row-1][col]:
        count += 1

    if row+1 < len(domain) and CellState.BULB in domain[row+1][col]:
        count += 1

    if col-1 >= 0 and CellState.BULB in domain[row][col-1]:
        count += 1

    if col+1 < len(domain[0]) and CellState.BULB in domain[row][col+1]:
        count += 1

    return count == 3


def place_bulb_around_wall_3(puzzle, row, col, domain_of_empty_cell, empty_cells):

    """
    # Place 3 bulbs around a wall with number 3
    # The given wall is ensured to have exactly 3 empty space around it
    # While placing bulb, check if all domain size of empty cell is still > 0,
    # there is no conflict in constraint (e.i. an empty cell that only have value domain '_' yet must be placed a bulb on"
    # and the state of the puzzle is still valid (no 2 bulbs seeing each other)
    # Return true if everything is satisfied
    :param puzzle:
    :param row:
    :param col:
    :param domain_of_empty_cell:
    :param empty_cell:
    :return:
    """

    true_count = [False, False, False]
    count = 0

    if row-1 >= 0 and CellState.BULB in domain_of_empty_cell[row-1][col]:
        puzzle[row - 1][col] = CellState.BULB

        # Sometimes we are re-assigning bulb a cell that already has a bulb placed on it
        # So we gotta check if this cell is still on empty_cells
        if [row - 1, col] in empty_cells:
            empty_cells.remove([row - 1, col])

        domain_change(domain_of_empty_cell, row - 1, col, CellState.BULB)
        if is_state_valid(puzzle) and check_no_empty_domain(domain_of_empty_cell, empty_cells):
            count += 1

    if row+1 < len(puzzle) and CellState.BULB in domain_of_empty_cell[row+1][col]:
        puzzle[row + 1][col] = CellState.BULB

        if [row + 1, col] in empty_cells:
            empty_cells.remove([row + 1, col])

        domain_change(domain_of_empty_cell, row + 1, col, CellState.BULB)
        if is_state_valid(puzzle) and check_no_empty_domain(domain_of_empty_cell, empty_cells):
            count += 1

    if col-1 >= 0 and CellState.BULB in domain_of_empty_cell[row][col-1]:
        puzzle[row][col-1] = CellState.BULB

        if [row , col-1] in empty_cells:
            empty_cells.remove([row , col-1])

        domain_change(domain_of_empty_cell, row, col-1, CellState.BULB)
        if is_state_valid(puzzle) and check_no_empty_domain(domain_of_empty_cell, empty_cells):
            count += 1

    if col+1 < len(puzzle[0]) and CellState.BULB in domain_of_empty_cell[row][col+1]:
        puzzle[row][col+1] = CellState.BULB

        if [row, col+1] in empty_cells:
            empty_cells.remove([row, col+1])

        domain_change(domain_of_empty_cell, row, col+1, CellState.BULB)
        if is_state_valid(puzzle) and check_no_empty_domain(domain_of_empty_cell, empty_cells):
            count += 1

    return count == 3


def wall_of_2_has_exactly_2_spots(domain, row, col):

    """
    # Given a wall of number 3, count if this wall has exactly 3 available cells around it to place bulb
    # Wall are not counted, and empty cells that doesn't have bulb in its domain are not counted

    :param domain: List[List[List[str]]] - the domain of each cell in the puzzle
    :param row: int - row coordinate of a wall with value 3
    :param col: int - col coordinate of a wall with value 3
    :return: bool
    """

    count = 0

    if row-1 >= 0 and CellState.BULB in domain[row-1][col]:
        count += 1

    if row+1 < len(domain) and CellState.BULB in domain[row+1][col]:
        count += 1

    if col-1 >= 0 and CellState.BULB in domain[row][col-1]:
        count += 1

    if col+1 < len(domain[0]) and CellState.BULB in domain[row][col+1]:
        count += 1

    return count == 2


def place_bulb_around_wall_2(puzzle, row, col, domain_of_empty_cell, empty_cells):

    """
    # Place 3 bulbs around a wall with number 3
    # The given wall is ensured to have exactly 3 empty space around it
    # While placing bulb, check if all domain size of empty cell is still > 0,
    # there is no conflict in constraint (e.i. an empty cell that only have value domain '_' yet must be placed a bulb on"
    # and the state of the puzzle is still valid (no 2 bulbs seeing each other)
    # Return true if everything is satisfied
    :param puzzle:
    :param row:
    :param col:
    :param domain_of_empty_cell:
    :param empty_cell:
    :return:
    """

    true_count = [False, False, False]
    count = 0

    if row-1 >= 0 and CellState.BULB in domain_of_empty_cell[row-1][col]:
        puzzle[row - 1][col] = CellState.BULB

        # Sometimes we are re-assigning bulb a cell that already has a bulb placed on it
        # So we gotta check if this cell is still on empty_cells
        if [row - 1, col] in empty_cells:
            empty_cells.remove([row - 1, col])

        domain_change(domain_of_empty_cell, row - 1, col, CellState.BULB)
        if is_state_valid(puzzle) and check_no_empty_domain(domain_of_empty_cell, empty_cells):
            count += 1

    if row+1 < len(puzzle) and CellState.BULB in domain_of_empty_cell[row+1][col]:
        puzzle[row + 1][col] = CellState.BULB

        if [row + 1, col] in empty_cells:
            empty_cells.remove([row + 1, col])

        domain_change(domain_of_empty_cell, row + 1, col, CellState.BULB)
        if is_state_valid(puzzle) and check_no_empty_domain(domain_of_empty_cell, empty_cells):
            count += 1

    if col-1 >= 0 and CellState.BULB in domain_of_empty_cell[row][col-1]:
        puzzle[row][col-1] = CellState.BULB

        if [row , col-1] in empty_cells:
            empty_cells.remove([row , col-1])

        domain_change(domain_of_empty_cell, row, col-1, CellState.BULB)
        if is_state_valid(puzzle) and check_no_empty_domain(domain_of_empty_cell, empty_cells):
            count += 1

    if col+1 < len(puzzle[0]) and CellState.BULB in domain_of_empty_cell[row][col+1]:
        puzzle[row][col+1] = CellState.BULB

        if [row, col+1] in empty_cells:
            empty_cells.remove([row, col+1])

        domain_change(domain_of_empty_cell, row, col+1, CellState.BULB)
        if is_state_valid(puzzle) and check_no_empty_domain(domain_of_empty_cell, empty_cells):
            count += 1

    return count == 2


def wall_of_1_has_exactly_1_spots(domain, row, col):

    """
    # Given a wall of number 3, count if this wall has exactly 3 available cells around it to place bulb
    # Wall are not counted, and empty cells that doesn't have bulb in its domain are not counted

    :param domain: List[List[List[str]]] - the domain of each cell in the puzzle
    :param row: int - row coordinate of a wall with value 3
    :param col: int - col coordinate of a wall with value 3
    :return: bool
    """

    count = 0

    if row-1 >= 0 and CellState.BULB in domain[row-1][col]:
        count += 1

    if row+1 < len(domain) and CellState.BULB in domain[row+1][col]:
        count += 1

    if col-1 >= 0 and CellState.BULB in domain[row][col-1]:
        count += 1

    if col+1 < len(domain[0]) and CellState.BULB in domain[row][col+1]:
        count += 1

    return count == 1


def place_bulb_around_wall_1(puzzle, row, col, domain_of_empty_cell, empty_cells):

    """
    # Place 3 bulbs around a wall with number 3
    # The given wall is ensured to have exactly 3 empty space around it
    # While placing bulb, check if all domain size of empty cell is still > 0,
    # there is no conflict in constraint (e.i. an empty cell that only have value domain '_' yet must be placed a bulb on"
    # and the state of the puzzle is still valid (no 2 bulbs seeing each other)
    # Return true if everything is satisfied
    :param puzzle:
    :param row:
    :param col:
    :param domain_of_empty_cell:
    :param empty_cell:
    :return:
    """

    true_count = [False, False, False]
    count = 0

    if row-1 >= 0 and CellState.BULB in domain_of_empty_cell[row-1][col]:
        puzzle[row - 1][col] = CellState.BULB

        # Sometimes we are re-assigning bulb a cell that already has a bulb placed on it
        # So we gotta check if this cell is still on empty_cells
        if [row - 1, col] in empty_cells:
            empty_cells.remove([row - 1, col])

        domain_change(domain_of_empty_cell, row - 1, col, CellState.BULB)
        if is_state_valid(puzzle) and check_no_empty_domain(domain_of_empty_cell, empty_cells):
            count += 1

    if row+1 < len(puzzle) and CellState.BULB in domain_of_empty_cell[row+1][col]:
        puzzle[row + 1][col] = CellState.BULB

        if [row + 1, col] in empty_cells:
            empty_cells.remove([row + 1, col])

        domain_change(domain_of_empty_cell, row + 1, col, CellState.BULB)
        if is_state_valid(puzzle) and check_no_empty_domain(domain_of_empty_cell, empty_cells):
            count += 1

    if col-1 >= 0 and CellState.BULB in domain_of_empty_cell[row][col-1]:
        puzzle[row][col-1] = CellState.BULB

        if [row , col-1] in empty_cells:
            empty_cells.remove([row , col-1])

        domain_change(domain_of_empty_cell, row, col-1, CellState.BULB)
        if is_state_valid(puzzle) and check_no_empty_domain(domain_of_empty_cell, empty_cells):
            count += 1

    if col+1 < len(puzzle[0]) and CellState.BULB in domain_of_empty_cell[row][col+1]:
        puzzle[row][col+1] = CellState.BULB

        if [row, col+1] in empty_cells:
            empty_cells.remove([row, col+1])

        domain_change(domain_of_empty_cell, row, col+1, CellState.BULB)
        if is_state_valid(puzzle) and check_no_empty_domain(domain_of_empty_cell, empty_cells):
            count += 1

    return count == 1


def pre_process_puzzle(puzzle, domain_of_empty_cell, empty_cell):

    """
    # Pre-processing the given puzzle by placing bulb at sure-place
    # For each bulb that we place, correspondingly reduce the domain of related empty cells
    # Return True if the pre-processed puzzle is still solvable -
    # (still in valid state and none of the empty cell has domain of size 0)
    # or no conflict of constraints happen
    :param puzzle: List[List[str]]
    :return: bool
    """

    wall_cell = get_wall_cells(puzzle)

    # First, reduce the domain space of all cell next to wall 0
    for cell in wall_cell:
        row = cell[0]
        col = cell[1]

        # If seeing a wall of number 0, reduce domain of all empty walls around it
        if int(puzzle[row][col]) == 0:

            # The upper row is still in the puzzle, and the upper cell is an empty cell
            if row - 1 >= 0 and puzzle[row-1][col] == CellState.EMPTY:
                take_bulb_from_cell_domain(domain_of_empty_cell, row-1, col)

            if row + 1 < len(puzzle) and puzzle[row+1][col] == CellState.EMPTY:
                take_bulb_from_cell_domain(domain_of_empty_cell, row+1, col)

            if col - 1 >= 0 and puzzle[row][col-1] == CellState.EMPTY:
                take_bulb_from_cell_domain(domain_of_empty_cell, row, col-1)

            if col + 1 < len(puzzle[row]) and puzzle[row][col+1] == CellState.EMPTY:
                take_bulb_from_cell_domain(domain_of_empty_cell, row, col+1)

    # Then place bulb around wall with value 4
    for cell in wall_cell:
        row = cell[0]
        col = cell[1]

        # If seeing a wall of number 4, check for the domain of empty cells around it
        # If the domain of cells around it allow bulb, place bulb into them
        # else, this puzzle is unsolvable
        if int(puzzle[row][col]) == 4:

            # If true, 4 is at the edge of the puzzle and therefore, cannot place 4 bulbs
            if row - 1 < 0 or col - 1 < 0 or row + 1 >= len(puzzle) or col + 1 >= len(puzzle[row]):
                return False
            else:
                success = place_bulb_around_wall_4(puzzle, row, col, domain_of_empty_cell, empty_cell)
            if not success:

                return False;

    # Then place bulb around wall with value 3
    for cell in wall_cell:
        row = cell[0]
        col = cell[1]

        # If seeing a wall of number 3, check for the domain of empty cells around it
        # If the domain of cells around it allow exactly 3 bulbs, place bulb into them
        # else, this puzzle is unsolvable
        if int(puzzle[row][col]) == 3:

            if wall_of_3_has_exactly_3_spots(domain_of_empty_cell, row, col):
                success = place_bulb_around_wall_3(puzzle, row, col, domain_of_empty_cell, empty_cell)
                if not success:
                    return False

    # Then place bulb around wall with value 2
    for cell in wall_cell:
        row = cell[0]
        col = cell[1]

        # If seeing a wall of number 2, check for the domain of empty cells around it
        # If the domain of cells around it allow exactly 2 bulbs, place bulb into them
        # else, this puzzle is unsolvable
        if int(puzzle[row][col]) == 2:

            if wall_of_2_has_exactly_2_spots(domain_of_empty_cell, row, col):
                success = place_bulb_around_wall_2(puzzle, row, col, domain_of_empty_cell, empty_cell)
                if not success:
                    return False

    # Then place bulb around wall with value 1
    for cell in wall_cell:
        row = cell[0]
        col = cell[1]

        # If seeing a wall of number 1, check for the domain of empty cells around it
        # If the domain of cells around it allow bulb, place bulb into them
        # else, this puzzle is unsolvable
        if int(puzzle[row][col]) == 1:

            if wall_of_1_has_exactly_1_spots(domain_of_empty_cell, row, col):
                success = place_bulb_around_wall_1(puzzle, row, col, domain_of_empty_cell, empty_cell)
                if not success:
                    return False

    return True


# call necessary methods/algorithms to solve the puzzle as required.
def solve_puzzle(puzzle, heuristic):

    empty_cells = get_empty_cells(puzzle)
    domain_of_empty_cell = make_empty_cell_domain(puzzle)

    status = pre_process_puzzle(puzzle, domain_of_empty_cell, empty_cells)

    wall_cells = get_wall_cells(puzzle)

    if status:
        print("Chosen heuristic: {}.".format(heuristic))
        return forward_checking(puzzle, domain_of_empty_cell, empty_cells, wall_cells, heuristic)
    else:
        return 'failure'


# receive input, process input and call necessary methods to solve the puzzle.
def main(argv=None):

    if argv is None:
        argv = sys.argv[1:]

        arg_parser = argparse.ArgumentParser(add_help=False)
        arg_parser.add_argument('--p', action='store', dest='file_name', type=str, default='test.txt')
        arg_parser.add_argument('--h', action='store', dest='heuristic', type=str, default='H3')

        arguments = arg_parser.parse_args(argv)
        file_name = arguments.file_name
        heuristic = arguments.heuristic
        puzzle_dict = read_file(file_name)

        for i in puzzle_dict.keys():

            #node_count = 0
            puzzle = puzzle_dict[i]

            if i != 0:
                print()

            print('The puzzle is:')
            print_puzzle(puzzle)

            starting_time = time.time()
            solution = solve_puzzle(puzzle, heuristic)
            ending_time = time.time()

            print()

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
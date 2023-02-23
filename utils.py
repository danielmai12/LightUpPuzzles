import os


class CellState:
    BULB = 'b'
    EMPTY = '_'


def read_file(filename):
    file = open(os.getcwd() + '/data/' + filename)
    puzzle_dict = {}
    count = 0
    for line in file:
        if line[0] != "#":
            line = line.split()
            rows, cols = int(line[0].strip()), int(line[1].strip())
            puzzle_dict[count] = [[0 for x in range(cols)] for y in range(rows)]

            for row in range(rows):
                line = file.readline()
                for col in range(cols):
                    cell = line[col]
                    if cell.isnumeric():
                        cell = int(cell)
                    puzzle_dict[count][row][col] = cell
        count += 1

    return puzzle_dict


def print_puzzle(puzzle):
    for row in range(len(puzzle)):
        for col in range(len(puzzle[0])):
            if col == len(puzzle[0]) - 1:
                print(puzzle[row][col])
            else:
                print(puzzle[row][col], end='')


# Given the current state of the curr_state, with newly placed bulbs,
# light up all cells in the same row and col that is not obstructed by wall using * symbols
def light_state(curr_state):
    """
    :param curr_state:
    :return:
    """
    # Iterate through each cell in the current state
    for row in range( len(curr_state) ):
        for col in range( len(curr_state[row]) ):
            if curr_state[row][col] == 'b':
                # At the position of the light bulb, light up all
                travel_dist = 1;

                while row - travel_dist >= 0 and (curr_state[row - travel_dist][col] == '_' or curr_state[row - travel_dist][col] == '*'):
                    curr_state[row - travel_dist][col] = '*'
                    travel_dist += 1
                travel_dist = 1
                while row + travel_dist < len(curr_state) and (curr_state[row + travel_dist][col] == '_' or curr_state[row + travel_dist][col] == '*'):
                    curr_state[row + travel_dist][col] = '*'
                    travel_dist += 1
                travel_dist = 1
                while col - travel_dist >= 0 and (curr_state[row][col - travel_dist] == '_' or curr_state[row][col - travel_dist] == '*'):
                    curr_state[row][col - travel_dist] = '*'
                    travel_dist += 1
                travel_dist = 1
                while col + travel_dist < len(curr_state[row]) and (curr_state[row][col + travel_dist] == '_' or curr_state[row][col + travel_dist] == '*'):
                    curr_state[row][col + travel_dist] = '*'
                    travel_dist += 1


# Given the position of a bulb, count the number of cells that bulb can light up
# and return this number
def count_should_be_lit_cells(curr_state: 'List[List[str]]', row: int, col: int) -> int:
    """
    :param curr_state: the current state of the puzzle
    :param row: the row index of the bulb
    :param col: the col index of the bulb
    :return: Number of cells the bulb at row col can light up
    """
    count = 0
    upper_row = row - 1
    lower_row = row + 1
    col_left = col - 1
    col_right = col + 1

    ## loop through all four directions

    # Going up
    while upper_row >= 0 and (curr_state[upper_row][col] == '_' or curr_state[upper_row][col] == '*'):
        if curr_state[upper_row][col] == '_':
            count += 1
        upper_row -= 1

    # Going down
    while lower_row < len(curr_state) and (
            curr_state[lower_row][col] == '_' or curr_state[lower_row][col] == '*'):
        if curr_state[lower_row][col] == '_':
            count += 1
        lower_row += 1

    # To the left
    while col_left >= 0 and (curr_state[row][col_left] == '_' or curr_state[row][col_left] == '*'):
        if curr_state[row][col_left] == '_':
            count += 1
        col_left -= 1

    # To the right
    while col_right < len(curr_state[0]) and (
            curr_state[row][col_right] == '_' or curr_state[row][col_right] == '*'):
        if curr_state[row][col_right] == '_':
            count += 1
        col_right += 1

    return count


def has_valid_adjacent_lights(puzzle, row, col):
    # check if a cell with a number has the correct number of adjacent lights
    count = 0
    rows = len(puzzle)
    cols = len(puzzle)

    if row > 0 and puzzle[row - 1][col] == CellState.BULB:  # down
        count += 1
    if row < rows - 1 and puzzle[row + 1][col] == CellState.BULB:  # up
        count += 1
    if col > 0 and puzzle[row][col - 1] == CellState.BULB:  # left
        count += 1
    if col < cols - 1 and puzzle[row][col + 1] == CellState.BULB:  # right
        count += 1

    return puzzle[row][col] == count


def num_adjacent_walls(puzzle, row, col):
    # count how many walls surround the given cell (row, col)
    num_walls = 0
    rows = len(puzzle)
    cols = len(puzzle)

    if row > 0 and puzzle[row - 1][col].isdigit():  # down
        num_walls += 1
    if row < rows - 1 and puzzle[row + 1][col].isdigit():  # up
        num_walls += 1
    if col > 0 and puzzle[row][col - 1].isdigit():  # left
        num_walls += 1
    if col < cols - 1 and puzzle[row][col + 1].isdigit():  # right
        num_walls += 1

    return num_walls


def edge_corner_constraints(puzzle, row, col):
    """
    Check if the given cell (row, col) is in edge/corner
        - not an edge/corner = 0 (no constraint)
        - edge = 1
        - corner = 2
    :return: its constraint level
    """
    constraint = 0
    rows = len(puzzle)
    cols = len(puzzle)

    if row == 0 or row == rows - 1 or col == 0 or col == cols - 1:  # edge
        constraint = 1

    if (row == 0 or row == rows - 1) and (col == 0 or col == cols - 1):  # corner
        constraint = 2

    return constraint

# Return True if map is lit up entirely, False otherwise
# Removing all * symbols to be printed out.
def map_is_lit(curr_state):

    is_lit_up = True

    # Iterate through all cells to look for _ symbol
    # if we  see _, solution is not complete

    for row in range(len(curr_state)):
        for col in range(len(curr_state[row])):
            if curr_state[row][col] == '_':
                lit_up = False
            elif curr_state[row][col] == '*':
                curr_state[row][col] = '_'

    return is_lit_up



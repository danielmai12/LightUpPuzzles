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

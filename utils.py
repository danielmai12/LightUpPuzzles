import os


def read_file(filename):
    file = open(os.getcwd() + '/data/' + filename)
    puzzle_dict = {}
    count = 0
    for line in file:
        if line[0] != "#":
            count += 1
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
    return puzzle_dict


def print_puzzle(puzzle):
    for row in range(len(puzzle)):
        for col in range(len(puzzle[0])):
            if col == len(puzzle[0]) - 1:
                print(puzzle[row][col])
            else:
                print(puzzle[row][col], end='')


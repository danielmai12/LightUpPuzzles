from utils import *

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
    global num_nodes
    num_nodes += 1
    # printing solving status
    if num_nodes < 10000:
        if num_nodes % 3 == 0:
            print('\rProcessing.')
        if num_nodes % 3 == 1:
            print('\rProcessing..')
        if num_nodes % 3 == 2:
            print('\rProcessing...')
    if num_nodes % 10000 == 0:
        print('\rAlready processed {} nodes.'.format(num_nodes))
    if num_nodes == 5000000:
        return 'Too many nodes. Timeout!'
    if validate_wall_condition(puzzle):
        return puzzle
    # backtrack if this cannot be part of a valid solution
    if len(empty_cells) == 0 and check_curr_state(puzzle, empty_cells):
        return 'backtrack'

    chosen_cells, chosen_cell = [], []
    # check the input to see what heuristic should be used
    if heuristic == 'most_constrained':
        chosen_cells = find_most_constrained(puzzle, empty_cells)
    elif heuristic == 'most_constraining':
        chosen_cells = find_most_constraining(puzzle, empty_cells)
    elif heuristic == 'hybrid':
        chosen_cells = hybrid_heuristic(puzzle, empty_cells)
    else:
        print('\n*** ERROR *** Heuristic must be either "most_constrained", "most_constraining" or "hybrid".')
        return 'stop'
    if len(chosen_cells) >= 1:
        chosen_cell = chosen_cells[random.randint(0, len(chosen_cells) - 1)]

    # remove the chosen cell from the list of potential bulb cells later
    empty_cells.remove(chosen_cell)

    r, c = chosen_cell[0], chosen_cell[1]
    for val in domain:
        puzzle[r][c] = val
        if (val != '_' and can_bulb_be_here(puzzle, r, c)) or val == '_':
            result = forward_checking(puzzle, domain, empty_cells, heuristic)
            if result != 'backtrack':
                return result

    empty_cells.append(chosen_cell)
    return 'backtrack'


# get all the empty cells in the map, which are potential places for bulbs.
def get_empty_cells(puzzle: List[List[str]]) -> List[List[int]]:
    empty_cells = []
    for r in range(len(puzzle)):
        for c in range(len(puzzle[r])):
            if puzzle[r][c] == '_':
                empty_cells.append([r, c])
    return empty_cells


# some places in the map are certain to be bulbs because of some constraints, for example neighbours of a wall 4 have to
# bulbs, neighbours of wall 3 in the edge, neighbours of wall 2 in the corner, or the amount of empty neighbours of a
# wall is exactly the same as its number.
def place_must_have_bulbs(puzzle: List[List[str]], empty_cells: List[List[int]]) -> List[List[int]]:
    stop = False
    while not stop:
        new_bulb_placed = False
        for wall in library.valid_wall:

            sure_variable = library.generate_valid_neighbours(wall[0], wall[1], len(puzzle), puzzle)
            count_bulbs = 0
            count_empty_cells = 0
            count_stars = 0
            for var in sure_variable:
                if puzzle[var[0]][var[1]] == 'b':
                    count_bulbs += 1
                elif puzzle[var[0]][var[1]] == '_':
                    count_empty_cells += 1
                elif puzzle[var[0]][var[1]] == '*':
                    count_stars += 1
            # if the amount of empty neighbours of a wall is exactly the same as its number, place bulbs
            if count_empty_cells > 0 and count_empty_cells == int(puzzle[wall[0]][wall[1]]) - count_bulbs:
                for var in sure_variable:
                    if puzzle[var[0]][var[1]] == '_':
                        puzzle[var[0]][var[1]] = 'b'
                        empty_cells.remove(var)

                new_bulb_placed = True
                light_map_up(puzzle)
        if not new_bulb_placed:
            stop = True

    # remove already lit up cells from the list of potential cells to place a bulb
    variables = copy.deepcopy(empty_cells)
    for cell in variables:
        if puzzle[cell[0]][cell[1]] == '*':
            empty_cells.remove(cell)

    return empty_cells


# remove all cells surrounding a wall 0 from the list of places for bulbs, as there can't be any bulbs surrouding
# a wall 0
def remove_zero_wall_neighbours(puzzle: List[List[str]], empty_cells: List[List[int]]):
    invalid_neighbours = []
    # remove all neighbours of a zero wall
    for x in range(len(library.invalid_wall)):
        invalid_neighbours.extend(library.generate_valid_neighbours(library.invalid_wall[x][0],
                                                                    library.invalid_wall[x][1], len(puzzle), puzzle))
    for x in range(len(invalid_neighbours)):
        if invalid_neighbours[x] in empty_cells:
            empty_cells.remove(invalid_neighbours[x])


# do some pre-processing to decrease the number of variables to be considered
def pre_process(puzzle: List[List[str]], empty_cells: List[List[int]]):
    empty_cells = place_must_have_bulbs(puzzle, empty_cells)
    remove_zero_wall_neighbours(puzzle, empty_cells)
    # TODO: Remove this print line
    library.print_puzzle(puzzle)
    is_map_lit_up_and_clean_map(puzzle)


# call necessary methods/algorithms to solve the puzzle as required.
def solve(puzzle: List[List[str]], heuristic: str):
    domain = ('b', '_')
    non_assigned = get_empty_cells(puzzle)
    pre_process(puzzle, non_assigned)
    print("Chosen heuristic: {}.".format(heuristic))
    return forward_checking(puzzle, domain, non_assigned, heuristic)


# receive input, process input and call necessary methods to solve the puzzle.
def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--heuristic', action='store', dest='heuristic', type=str, default='most_constrained')

    arguments = arg_parser.parse_args(argv)

    puzzle = read_puzzle()

    starting_time = time.time()
    solution = solve(puzzle, arguments.heuristic)
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
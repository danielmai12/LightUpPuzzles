from utils import *


def h1(curr_state, available_cells):
    """
    Find most constrained: Selects the node with the least remaining options as the next move based on:
        - number of walls surrounding the cell
        - if it is in middle or edge/corner
        - if its neighbor
    :return:
    """
    curr_most_constrained = (-1, []) # (num_constraints, [list cells most constrained])

    for cell in available_cells:
        adjacent_walls = num_adjacent_walls(curr_state, cell[0], cell[1])  # check to see how many adjacent walls
        location_constraints = edge_corner_constraints(curr_state, cell[0], cell[1])  # check the location constraints

        constraints = adjacent_walls + location_constraints

        if constraints == curr_most_constrained[0]:
            curr_most_constrained[1].append(cell)
        if constraints > curr_most_constrained[0]:
            curr_most_constrained = (constraints, [cell])

    return curr_most_constrained


def h2(curr_state: 'List[List[str]]', available_cells: 'List[List[int]]' ):
    """
    Find most constraining
    :return:
    """

    cells = []
    max_count = 0

    light_state(curr_state)

    for cell in available_cells:
        to_be_lit_up = count_should_be_lit_cells(curr_state, cell[0], cell[1])
        if to_be_lit_up > max_count:
            cells = [cell]
            max_count = to_be_lit_up
        elif to_be_lit_up == max_count:
            cells.append(cell)
    map_is_lit(curr_state)
    return cells


def h3(curr_state):
    """
    Hybrid
    :return:
   """



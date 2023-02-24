from utils import *


def h1(curr_state, available_cells):
    """
    Find most constrained: Select the cell/node with the least remaining options as the next move based on:
        - number of walls surrounding the cell
        - if it is in middle or edge/corner
        - if its neighbor constraints (how many has been lit up?)
    """
    curr_most_constrained = (-1, [])  # (num_constraints, [list cells most constrained])
    light_up_puzzle(curr_state)

    for cell in available_cells:
        adjacent_walls = num_adjacent_walls(curr_state, cell[0], cell[1])  # check to see how many adjacent walls
        location_constraints = edge_corner_constraints(curr_state, cell[0], cell[1])  # check the location constraints
        light_constraints = neighbor_constraints(curr_state, cell[0], cell[1])

        constraints = adjacent_walls + location_constraints + light_constraints

        if constraints == curr_most_constrained[0]:
            curr_most_constrained[1].append(cell)
        if constraints > curr_most_constrained[0]:
            curr_most_constrained = (constraints, [cell])
    unlit_map(curr_state)

    return curr_most_constrained


def h2(curr_state, available_cells):
    """
    Find most constraining: Select a cell/node that causes most reduction in options for other cells/nodes by:
        - Counting the num cells that (potential) bulb can light up - choose the maximum
    """

    cells = []
    max_count = 0

    light_up_puzzle(curr_state)

    for cell in available_cells:
        to_be_lit_up = num_cells_light(curr_state, cell[0], cell[1])
        if to_be_lit_up > max_count:
            cells = [cell]
            max_count = to_be_lit_up
        elif to_be_lit_up == max_count:
            cells.append(cell)
    unlit_map(curr_state)

    return cells


def h3(curr_state, available_cells):
    """
    Hybrid: This heuristics combine both H1 and H2.
    """
    target_cells = h1(curr_state, available_cells)
    if len(target_cells) > 1:
        target_cells = h2(curr_state, target_cells)

    return target_cells

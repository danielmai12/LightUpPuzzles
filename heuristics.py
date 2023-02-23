import utils

def h1(current_state):
    """
    Find most constrained
    :return:
    """


def h2(current_state: 'List[List[str]]', available_cells: 'List[List[int]]' ):
    """
    Find most constraining
    :return:
    """

    cells = []
    max_count = 0

    utils.light_state(current_state)

    for cell in available_cells:
        to_be_lit_up = count_should_be_lit_cells(current_state, cell[0], cell[1])
        if to_be_lit_up > max_count:
            cells = [cell]
            max_count = to_be_lit_up
        elif to_be_lit_up == max_count:
            cells.append(cell)
    is_map_lit_up_and_clean_map(current_state)
    return cells


def h3(current_state):
    """
    Hybrid
    :return:
   """



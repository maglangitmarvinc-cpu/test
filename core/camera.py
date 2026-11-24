"""Screen mapping for the game's raised, faux-depth board."""
from settings import BOARD_LEFT, BOARD_TOP, CELL

def grid_to_screen(x,y):
    """Map a board cell into the raised board's screen coordinates."""
    return int(BOARD_LEFT+(x+.5)*CELL), int(BOARD_TOP+(y+.5)*CELL)

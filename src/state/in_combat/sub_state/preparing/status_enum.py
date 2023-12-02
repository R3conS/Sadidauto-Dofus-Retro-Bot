from enum import Enum


class Status(Enum):
    
    SUCCESSFULLY_MOVED_TO_DUMMY_CELLS = "successfully_moved_to_dummy_cells"
    FAILED_TO_MOVE_TO_DUMMY_CELLS = "failed_to_move_to_dummy_cells"
    FAILED_TO_MOVE_TO_STARTING_CELLS = "failed_to_move_to_starting_cells"
    NO_DUMMY_CELLS_ON_THIS_MAP = "no_dummy_cells_on_this_map"
    FAILED_TO_PREPARE = "failed_to_prepare"
    SUCCESSFULLY_MOVED_TO_CELL = "successfully_moved_to_cell"
    FAILED_TO_MOVE_TO_CELL = "failed_to_move_to_cell"

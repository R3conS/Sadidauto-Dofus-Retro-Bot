from enum import Enum


class Status(Enum):

    SUCCESSFULLY_MOVED_TO_CELL = "successfully_moved_to_cell"
    FAILED_TO_MOVE_TO_CELL = "failed_to_move_to_cell"
    FIGHT_RESULTS_WINDOW_DETECTED = "fight_results_window_detected"
    CHARACTERS_TURN_DETECTED = "characters_turn_detected"

from enum import Enum


class Status(Enum):
    
    SUCCESSFULLY_MOVED_TO_DUMMY_CELLS = "successfully_moved_to_dummy_cells"
    SUCCESSFULLY_MOVED_TO_CELL = "successfully_moved_to_cell"
    SUCCESSFULLY_TURNED_ON_FIGHT_LOCK = "successfully_turned_on_fight_lock"
    SUCCESSFULLY_TURNED_ON_TACTICAL_MODE = "successfully_turned_on_tactical_mode"
    SUCCESSFULLY_FINISHED_PREPARING = "successfully_finished_preparing"
    SUCCESSFULLY_CLICKED_READY_BUTTON = "successfully_clicked_ready_button"
    FAILED_TO_MOVE_TO_DUMMY_CELLS = "failed_to_move_to_dummy_cells"
    FAILED_TO_MOVE_TO_STARTING_CELLS = "failed_to_move_to_starting_cells"
    FAILED_TO_MOVE_TO_CELL = "failed_to_move_to_cell"
    FAILED_TO_FINISH_PREPARING = "failed_to_prepare"
    FAILED_TO_TURN_ON_FIGHT_LOCK = "failed_to_turn_on_fight_lock"
    FAILED_TO_TURN_ON_TACTICAL_MODE = "failed_to_turn_on_tactical_mode"
    FAILED_TO_GET_FIGHT_LOCK_ICON_POS = "failed_to_get_fight_lock_icon_pos"
    FAILED_TO_GET_TACTICAL_MODE_ICON_POS = "failed_to_get_tactical_mode_icon_pos"
    FAILED_TO_GET_READY_BUTTON_POS = "failed_to_get_ready_button_pos"
    TIMED_OUT_WHILE_TURNING_ON_FIGHT_LOCK = "timed_out_while_turning_on_fight_lock"
    TIMED_OUT_WHILE_TURNING_ON_TACTICAL_MODE = "timed_out_while_turning_on_tactical_mode"
    TIMED_OUT_WHILE_CLICKING_READY_BUTTON = "timed_out_while_clicking_ready_button"
    FIGHT_LOCK_IS_ALREADY_ON = "fight_lock_is_already_on"
    TACTICAL_MODE_IS_ALREADY_ON = "tactical_mode_is_already_on"
    NO_DUMMY_CELLS_ON_THIS_MAP = "no_dummy_cells_on_this_map"

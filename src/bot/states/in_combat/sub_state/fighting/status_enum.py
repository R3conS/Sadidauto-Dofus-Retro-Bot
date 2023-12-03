from enum import Enum


class Status(Enum):

    SUCCESSFULLY_DETECTED_TURN = "successfully_detected_turn"
    TIMED_OUT_WHILE_DETECTING_TURN = "timed_out_while_detecting_turn"

    SUCCESSFULLY_SHRUNK_TURN_BAR = "successfully_shrunk_turn_bar"
    TIMED_OUT_WHILE_SHRINKING_TURN_BAR = "timed_out_while_shrinking_turn_bar"
    TURN_BAR_ALREADY_SHRUNK = "turn_bar_already_shrunk"

    SUCCESSFULLY_TURNED_ON_TACTICAL_MODE = "successfully_turned_on_tactical_mode"
    FAILED_TO_GET_TACTICAL_MODE_TOGGLE_ICON_POS = "failed_to_get_tactical_mode_toggle_icon_pos"
    TIMED_OUT_WHILE_TURNING_ON_TACTICAL_MODE = "timed_out_while_turning_on_tactical_mode"

    SUCCESSFULLY_DISABLED_MODELS = "successfully_disabled_models"
    FAILED_TO_GET_MODELS_TOGGLE_ICON_POS = "failed_to_get_models_toggle_icon_pos"
    TIMED_OUT_WHILE_DISABLING_MODELS = "timed_out_while_disabling_models"
    MODELS_TOGGLE_ICON_NOT_VISIBLE = "models_toggle_icon_not_visible"

    SUCCESSFULLY_HANDLED_FIGHT_PREFERENCES = "successfully_handled_fight_preferences"

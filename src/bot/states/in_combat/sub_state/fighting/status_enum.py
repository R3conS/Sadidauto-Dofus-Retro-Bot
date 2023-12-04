from enum import Enum


class Status(Enum):

    SUCCESSFULLY_FINISHED_FIGHTING = "successfully_finished_fighting"
    FAILED_TO_FINISH_FIGHTING = "failed_to_finish_fighting"

    SUCCESSFULLY_DETECTED_TURN = "successfully_detected_turn"
    TIMED_OUT_WHILE_DETECTING_TURN = "timed_out_while_detecting_turn"

    SUCCESSFULLY_SHRUNK_TURN_BAR = "successfully_shrunk_turn_bar"
    SUCCESSFULLY_UNSHRUNK_TURN_BAR = "successfully_unshrunk_turn_bar"
    TIMED_OUT_WHILE_SHRINKING_TURN_BAR = "timed_out_while_shrinking_turn_bar"
    TIMED_OUT_WHILE_UNSHRINKING_TURN_BAR = "timed_out_while_unshrinking_turn_bar"

    SUCCESSFULLY_TURNED_ON_TACTICAL_MODE = "successfully_turned_on_tactical_mode"
    FAILED_TO_GET_TACTICAL_MODE_TOGGLE_ICON_POS = "failed_to_get_tactical_mode_toggle_icon_pos"
    TIMED_OUT_WHILE_TURNING_ON_TACTICAL_MODE = "timed_out_while_turning_on_tactical_mode"
    TACTICAL_MODE_IS_ALREADY_ON = "tactical_mode_is_already_on"

    SUCCESSFULLY_DISABLED_MODELS = "successfully_disabled_models"
    FAILED_TO_GET_MODELS_TOGGLE_ICON_POS = "failed_to_get_models_toggle_icon_pos"
    TIMED_OUT_WHILE_DISABLING_MODELS = "timed_out_while_disabling_models"
    MODELS_TOGGLE_ICON_NOT_VISIBLE = "models_toggle_icon_not_visible"

    SUCCESSFULLY_SELECTED_SPELL = "successfully_selected_spell"
    FAILED_TO_GET_SPELL_POS = "failed_to_get_spell_pos"
    FAILED_TO_SELECT_SPELL = "failed_to_select_spell"

from src.logger import get_logger

log = get_logger()

from enum import Enum

from src.bot._states.in_combat._sub_states.sub_states_enum import State as InCombat_SubState
from src.utilities.general import screenshot_game_and_save_to_debug_folder


class ExceptionReason(Enum):

    UNSPECIFIED = 1 # Default.
    FAILED_TO_GET_MAP_COORDS = 2
    FAILED_TO_CHANGE_MAP = 3
    FAILED_TO_LOAD_SPELL_ICONS = 4
    FAILED_TO_GET_STARTING_SIDE_COLOR = 5
    FAILED_TO_GET_STARTING_CELL_COORDS = 6
    FAILED_TO_READ_DEFINED_TOOLTIP_PATTERN = 7


class RecoverableException(Exception):

    def __init__(
            self, 
            message, 
            reason=ExceptionReason.UNSPECIFIED,
            occured_in_sub_state: InCombat_SubState = None
        ):
        self.message = message
        self.reason = reason
        self.occured_in_sub_state = occured_in_sub_state
        log.error(f"RecoverableException: {message}")
        screenshot_game_and_save_to_debug_folder(f"RecoverableException - {self.reason}")
        super().__init__(message)


class UnrecoverableException(Exception):
    
    def __init__(self, message, reason=ExceptionReason.UNSPECIFIED):
        self.message = message
        self.reason = reason
        log.critical(f"UnrecoverableExpection: {message}")
        screenshot_game_and_save_to_debug_folder(f"UnrecoverableException - {self.reason}")
        super().__init__(message)


class InitializationException(Exception):

    def __init__(self, message):
        self.message = message
        log.critical(f"InitializationException: {message}")
        super().__init__(message)

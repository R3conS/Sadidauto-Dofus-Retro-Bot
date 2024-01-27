from src.logger import Logger
log = Logger.get_logger(Logger.DEBUG, True, True)

import os
from datetime import datetime
from enum import Enum

from cv2 import imwrite as save_image

from src.bot._states.in_combat._sub_states.sub_states_enum import State as InCombat_SubState
from src.utilities.screen_capture import ScreenCapture


def _take_a_screenshot(exception_reason):
    log.info("Screenshotting the game window ... ")
    sc = ScreenCapture.game_window()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
    path = os.path.join(Logger.get_logger_dir_path(), f"{timestamp} - {exception_reason}.png")
    save_image(path, sc)
    log.info("Screenshot saved.")


class ExceptionReason(Enum):

    UNSPECIFIED = 1 # Default.
    FAILED_TO_GET_MAP_COORDS = 2
    FAILED_TO_CHANGE_MAP = 3
    FAILED_TO_LOAD_SPELL_ICONS = 4


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
        _take_a_screenshot(self.reason)
        super().__init__(message)


class UnrecoverableException(Exception):
    
    def __init__(self, message, reason=ExceptionReason.UNSPECIFIED):
        self.message = message
        self.reason = reason
        log.critical(f"UnrecoverableExpection: {message}")
        _take_a_screenshot(self.reason)
        super().__init__(message)


if __name__ == "__main__":
    _take_a_screenshot(ExceptionReason.UNSPECIFIED)

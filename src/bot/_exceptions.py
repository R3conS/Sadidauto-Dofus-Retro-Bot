from src.logger import Logger
log = Logger.get_logger(Logger.DEBUG, True, True)

import os
from datetime import datetime
from enum import Enum

from cv2 import imwrite as save_image

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
    FAILED_TO_WAIT_FOR_LOADING_SCREEN_DURING_MAP_CHANGE = 3


class RecoverableException(Exception):

    def __init__(self, message, reason=ExceptionReason.UNSPECIFIED):
        self.message = message
        self.reason = reason
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

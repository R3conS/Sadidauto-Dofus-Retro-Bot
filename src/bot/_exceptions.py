from src.logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from enum import Enum


class ExceptionReason(Enum):

    UNSPECIFIED = 1 # Default.
    FAILED_TO_GET_MAP_COORDS = 2
    FAILED_TO_WAIT_FOR_LOADING_SCREEN_DURING_MAP_CHANGE = 3


class RecoverableException(Exception):

    def __init__(self, message, reason=ExceptionReason.UNSPECIFIED):
        self.message = message
        self.reason = reason
        log.error(f"RecoverableException: {message}")
        super().__init__(message)


class UnrecoverableException(Exception):
    
    def __init__(self, message=None):
        self.message = message
        log.critical(f"UnrecoverableExpection: {message}")
        super().__init__(message)

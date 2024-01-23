from src.logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)


class RecoverableException(Exception):
    def __init__(self, message):
        self.message = message
        log.error(f"RecoverableException: {message}")
        super().__init__(message)


class UnrecoverableException(Exception):
    def __init__(self, message=None):
        self.message = message
        log.critical(f"UnrecoverableExpection: {message}")
        super().__init__(message)

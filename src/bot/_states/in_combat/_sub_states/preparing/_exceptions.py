from src.logger import get_logger

log = get_logger()


class FailedToSelectDummyCell(Exception):

    def __init__(self, message):
        self.message = message
        log.error(f"{message}")
        super().__init__(message)


class FailedToSelectStartingCell(Exception):

    def __init__(self, message):
        self.message = message
        log.error(f"{message}")
        super().__init__(message)

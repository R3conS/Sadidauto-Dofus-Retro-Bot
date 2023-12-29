from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

class Exceptions:

    class FailedToOpenInterface(Exception):
        def __init__(self, message):
            self.message = message
            log.error(message)
            super().__init__(message)
    
    class FailedToCloseInterface(Exception):
        def __init__(self, message):
            self.message = message
            log.error(message)
            super().__init__(message)

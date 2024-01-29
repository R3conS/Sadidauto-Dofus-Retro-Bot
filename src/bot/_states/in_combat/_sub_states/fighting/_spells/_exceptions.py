from src.logger import Logger
log = Logger.get_logger()


class FailedToCastSpell(Exception):

    def __init__(self, message):
        self.message = message
        log.error(f"{message}")
        super().__init__(message)


class FailedToGetSpellIconPosition(Exception):
    
    def __init__(self, message):
        self.message = message
        log.error(f"{message}")
        super().__init__(message)


class FailedToDetectIfSpellIsSelected(Exception):
    
    def __init__(self, message):
        self.message = message
        log.error(f"{message}")
        super().__init__(message)


class SpellIsNotCastableOnProvidedPosition(Exception):
    
    def __init__(self, message):
        self.message = message
        log.error(f"{message}")
        super().__init__(message)


class FailedToDetectIfSpellWasCastSuccessfully(Exception):
    
    def __init__(self, message):
        self.message = message
        log.error(f"{message}")
        super().__init__(message)

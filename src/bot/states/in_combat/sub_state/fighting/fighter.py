from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from ._character_pos_finder import Finder as CharacterPosFinder


class Fighter:

    def __init__(self, script: str, character_name: str):
        self.__character_pos_finder = CharacterPosFinder(character_name)

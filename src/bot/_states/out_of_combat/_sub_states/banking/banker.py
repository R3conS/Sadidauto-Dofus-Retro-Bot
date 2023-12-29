from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from ._handlers.not_on_bank_map import Handler as Handler_NotOnBankMap
from ._handlers.on_bank_map import Handler as Handler_OnBankMap
from src.bot._map_changer.map_changer import MapChanger
from src.bot._states.out_of_combat._status_enum import Status


class Banker:

    def __init__(self, script: str, game_window_title: str):
        self._script = script
        self._game_window_title = game_window_title
        self._handler_not_on_bank_map = Handler_NotOnBankMap(self._script)
        self._handler_on_bank_map = Handler_OnBankMap(self._script, self._game_window_title)

    def bank(self):
        if not self._is_char_on_astrub_bank_map():
            if self._handler_not_on_bank_map.handle() == Status.FAILED_TO_RECALL:
                # Handle this error.
                return Status.FAILED_TO_FINISH_BANKING

        if self._is_char_on_astrub_bank_map():
            if self._handler_on_bank_map.handle() != Status.SUCCESSFULLY_FINISHED_BANKING:
                # Handle this error.
                return Status.FAILED_TO_FINISH_BANKING
        
        log.info("Successfully finished banking!")
        return Status.SUCCESSFULLY_FINISHED_BANKING

    @classmethod
    def _is_char_on_astrub_bank_map(cls):
        return MapChanger.get_current_map_coords() == "4,-16"

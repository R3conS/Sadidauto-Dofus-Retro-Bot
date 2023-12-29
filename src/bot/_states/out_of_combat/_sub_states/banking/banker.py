from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import os

from ._handlers.not_on_bank_map import Handler as Handler_NotOnBankMap
from ._handlers.on_bank_map import Handler as Handler_OnBankMap
from src.bot._map_changer.map_changer import MapChanger
from ._bank_data import Getter as BankData
from src.bot._exceptions import RecoverableException


class Banker:

    def __init__(self, script: str, game_window_title: str):
        self._script = script
        self._game_window_title = game_window_title
        self._handler_not_on_bank_map = Handler_NotOnBankMap(self._script)
        self._handler_on_bank_map = Handler_OnBankMap(self._script, self._game_window_title)
        self._bank_map = BankData.get_data(self._script)["bank_map"]

    def bank(self):
        while True:
            try:
                if not self._is_char_on_bank_map():
                    self._handler_not_on_bank_map.handle()
                else:
                    self._handler_on_bank_map.handle()
                    return
            except RecoverableException:
                # ToDo: Call recovery code and try again.
                # Perhaps surround the whole thing with a while that attempts
                # to recover a few times before raising UnrecoverableException.
                log.error("Recoverable exception occurred while banking. Exiting ...")
                os._exit(1)

    def _is_char_on_bank_map(self):
        return MapChanger.get_current_map_coords() == self._bank_map

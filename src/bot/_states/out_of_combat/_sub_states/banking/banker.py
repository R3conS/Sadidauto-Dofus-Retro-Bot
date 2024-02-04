from src.logger import Logger
log = Logger.get_logger()

from src.bot._map_changer.map_changer import MapChanger
from src.bot._states.out_of_combat._sub_states.banking._handlers.not_on_bank_map import Handler as Handler_NotOnBankMap
from src.bot._states.out_of_combat._sub_states.banking._handlers.on_bank_map import Handler as Handler_OnBankMap
from src.bot._states.out_of_combat._sub_states.banking.bank_data import Getter as BankDataGetter


class Banker:

    def __init__(self, script: str, game_window_title: str):
        self._script = script
        self._game_window_title = game_window_title
        self._handler_not_on_bank_map = Handler_NotOnBankMap(self._script)
        self._handler_on_bank_map = Handler_OnBankMap(self._script, self._game_window_title)
        self._bank_map = BankDataGetter.get_data(self._script)["bank_map"]

    def bank(self):
        while True:
            if not self._is_char_on_bank_map():
                self._handler_not_on_bank_map.handle()
            else:
                self._handler_on_bank_map.handle()
                return

    def _is_char_on_bank_map(self):
        return MapChanger.get_current_map_coords() == self._bank_map

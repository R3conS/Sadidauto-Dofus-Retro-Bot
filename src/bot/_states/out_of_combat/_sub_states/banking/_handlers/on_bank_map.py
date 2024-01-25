from src.logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import pyautogui as pyag

from src.bot._map_changer.map_changer import MapChanger
from src.bot._exceptions import RecoverableException
from src.bot._states.out_of_combat._sub_states.banking.bank_data import Getter as BankDataGetter
from src.bot._states.out_of_combat._sub_states.banking._vault.vault import Vault


class Handler:

    def __init__(self, script: str, game_window_title: str):
        self._script = script
        self._game_window_title = game_window_title
        self._vault = Vault(self._script, self._game_window_title)
        bank_data = BankDataGetter.get_data(self._script)
        self._enter_coords = bank_data["enter_coords"]
        self._exit_coords = bank_data["exit_coords"]
        self._is_char_inside_bank: callable = bank_data["is_char_inside_bank"]

    def handle(self):
        if not self._is_char_inside_bank():
            self._enter_bank()
        self._vault.open_vault()
        self._vault.deposit_all_tabs()
        self._vault.close_vault()
        self._leave_bank()

    def _enter_bank(self):
        log.info("Attempting to enter the bank ... ")
        pyag.keyDown('e')
        pyag.moveTo(*self._enter_coords)
        pyag.click()
        pyag.keyUp('e')
        MapChanger.wait_loading_screen_pass()
        if self._is_char_inside_bank():
            log.info("Successfully entered the bank.")
            return
        raise RecoverableException("Failed to enter the bank.")

    def _leave_bank(self):
        log.info("Attempting to leave the bank ... ")
        pyag.keyDown('e')
        pyag.moveTo(*self._exit_coords)
        pyag.click()
        pyag.keyUp('e')
        MapChanger.wait_loading_screen_pass()
        if not self._is_char_inside_bank():
            log.info("Successfully left the bank.")
            return 
        raise RecoverableException("Failed to leave the bank.")

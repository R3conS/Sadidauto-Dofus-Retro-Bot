from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import pyautogui as pyag

from .._vault.vault import Vault
from .._bank_data import Getter as BankData
from src.bot._map_changer.map_changer import MapChanger
from src.bot._states.out_of_combat._status_enum import Status


class Handler:

    def __init__(self, script: str, game_window_title: str):
        self._script = script
        self._game_window_title = game_window_title
        bank_data = BankData.get_data(self._script)
        self._enter_coords = bank_data["enter_coords"]
        self._exit_coords = bank_data["exit_coords"]
        self._vault = Vault(self._script, self._game_window_title)

    def handle(self):
        if not self._is_char_inside_astrub_bank():
            result = self._enter_astrub_bank()
            if result != Status.SUCCESSFULLY_ENTERED_BANK:
                return Status.FAILED_TO_FINISH_BANKING

        result = self._vault.open_vault()
        if result != Status.SUCCESSFULLY_OPENED_BANK_VAULT:
            return Status.FAILED_TO_FINISH_BANKING

        result = self._vault.deposit_all_tabs()
        if result != Status.SUCCESSFULLY_DEPOSITED_ALL_TABS:
            return Status.FAILED_TO_FINISH_BANKING
    
        result = self._vault.close_vault()
        if result != Status.SUCCESSFULLY_CLOSED_BANK_VAULT:
            return Status.FAILED_TO_FINISH_BANKING

        result = self._leave_astrub_bank()
        if result != Status.SUCCESSFULLY_LEFT_BANK:
            return Status.FAILED_TO_FINISH_BANKING
        
        return Status.SUCCESSFULLY_FINISHED_BANKING

    def _enter_astrub_bank(self):
        log.info("Attempting to enter the bank ... ")
        pyag.keyDown('e')
        pyag.moveTo(*self._enter_coords)
        pyag.click()
        pyag.keyUp('e')
        if MapChanger.has_loading_screen_passed():
            if self._is_char_inside_astrub_bank():
                log.info("Successfully entered the bank.")
                return Status.SUCCESSFULLY_ENTERED_BANK
            else:
                log.error("Failed to enter the bank.")
                return Status.FAILED_TO_ENTER_BANK
        else:
            log.error("Failed to detect loading screen after trying to enter the bank.")
            return Status.FAILED_TO_ENTER_BANK

    def _leave_astrub_bank(self):
        log.info("Attempting to leave the bank ... ")
        pyag.keyDown('e')
        pyag.moveTo(*self._exit_coords)
        pyag.click()
        pyag.keyUp('e')
        if MapChanger.has_loading_screen_passed():
            if not self._is_char_inside_astrub_bank():
                log.info("Successfully left the bank.")
                return Status.SUCCESSFULLY_LEFT_BANK
            else:
                log.error("Failed to leave the bank.")
                return Status.FAILED_TO_LEAVE_BANK
        else:
            log.error("Failed to detect loading screen after trying to leave the bank.")
            return Status.FAILED_TO_LEAVE_BANK

    @staticmethod
    def _is_char_inside_astrub_bank():
        return all((
            pyag.pixelMatchesColor(10, 587, (0, 0, 0)),
            pyag.pixelMatchesColor(922, 587, (0, 0, 0)),
            pyag.pixelMatchesColor(454, 90, (0, 0, 0)), 
            pyag.pixelMatchesColor(533, 99, (242, 240, 236)),
            pyag.pixelMatchesColor(491, 124, (239, 236, 232))
        ))

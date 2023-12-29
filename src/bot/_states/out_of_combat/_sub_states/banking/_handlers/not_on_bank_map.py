from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import pyautogui as pyag

from .._bank_data import Getter as BankData
from src.bot._map_changer.map_changer import MapChanger
from src.bot._exceptions import RecoverableException


class Handler:

    def __init__(self, script: str):
        self._script = script
        bank_data = BankData.get_data(self._script)
        self._bank_map = bank_data["bank_map"]
        self._zaap_map = bank_data["zaap_map"]
        self._no_recall_maps = bank_data["no_recall_maps"]

    def handle(self):
        self._recall()
        self._run_to_bank()

    def _recall(self):
        if self._is_char_on_no_recall_map():
            log.info("Character is close to the bank. No need to recall.")
            return
        if not self._does_char_have_recall_potion():
            log.info("Character does not have a recall potion.")
            return
        self._use_recall_potion()

    def _is_char_on_no_recall_map(self):
        return MapChanger.get_current_map_coords() in self._no_recall_maps

    def _use_recall_potion(self):
        pyag.moveTo(664, 725)
        pyag.click(clicks=2, interval=0.1)
        if MapChanger.has_loading_screen_passed():
            if MapChanger.get_current_map_coords() == self._zaap_map:
                log.info("Successfully recalled.")
                return
        raise RecoverableException("Failed to recall.")
    
    @staticmethod
    def _does_char_have_recall_potion():
        return pyag.pixelMatchesColor(664, 725, (120, 151, 154), tolerance=20)

    def _run_to_bank(self):
        path_to_bank = MapChanger.get_shortest_path(MapChanger.get_current_map_coords(), self._bank_map)
        while True:
            map_coords = MapChanger.get_current_map_coords()
            if map_coords == self._bank_map:
                log.info("Arrived at Astrub bank map.")
                return

            log.info(f"Running to bank. Current map coords: {map_coords}.")
            MapChanger.change_map(map_coords, path_to_bank[map_coords])
            if MapChanger.has_loading_screen_passed():
                continue
            raise RecoverableException("Failed to detect loading screen after changing map.")

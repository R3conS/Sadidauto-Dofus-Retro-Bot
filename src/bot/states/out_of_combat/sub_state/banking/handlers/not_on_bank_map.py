from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import pyautogui as pyag

from ..status_enum import Status
from ..map_data.getter import Getter as MapDataGetter
from src.bot.map_changer.map_changer import MapChanger


class Handler:

    def __init__(self, script):
        self._astrub_bank_map = "4,-16"
        self._astrub_zaap_map = "4,-19"
        self._movement_data = MapDataGetter.get_data_object(script).get_movement_data()
        self._no_recall_maps = ["4,-16", "4,-17", "4,-18", "4,-19"]

    def handle(self):
        if self._recall() == Status.FAILED_TO_DETECT_LOADING_SCREEN_AFTER_RECALL:
            return Status.FAILED_TO_RECALL
        if self._run_to_bank() == Status.ARRIVED_AT_ASTRUB_BANK_MAP:
            return Status.ARRIVED_AT_ASTRUB_BANK_MAP

    def _recall(self):
        if not self._is_char_on_no_recall_map():
            log.info("Character is not on a no-recall map. Attempting to recall ... ")
            if self._does_char_have_recall_potion():
                self._use_recall_potion()
                if MapChanger.has_loading_screen_passed():
                    if MapChanger.get_current_map_coords() == self._astrub_zaap_map:
                        log.info("Successfully recalled.")
                        return Status.SUCCESSFULLY_RECALLED
                else:
                    log.info("Failed to detect loading screen after recalling.")
                    return Status.FAILED_TO_DETECT_LOADING_SCREEN_AFTER_RECALL
            else:
                log.info("Character does not have a recall potion.")
                return Status.CHAR_DOESNT_HAVE_RECALL_POTION
        else:
            log.info("Character is close to the bank. No need to recall.")
            return Status.NO_NEED_TO_RECALL

    def _run_to_bank(self):
        while True:
            map_coords = MapChanger.get_current_map_coords()
            if map_coords == self._astrub_bank_map:
                log.info("Arrived at Astrub bank map.")
                return Status.ARRIVED_AT_ASTRUB_BANK_MAP

            log.info(f"Running to bank. Current map coords: {map_coords}.")
            MapChanger.change_map(map_coords, self._movement_data)
            if MapChanger.has_loading_screen_passed():
                continue
            log.info("Failed to detect loading screen after changing map.")
            return Status.FAILED_TO_DETECT_LOADING_SCREEN_AFTER_CHANGE_MAP

    def _is_char_on_no_recall_map(self):
        return MapChanger.get_current_map_coords() in self._no_recall_maps

    @staticmethod
    def _use_recall_potion():
        pyag.moveTo(664, 725)
        pyag.click(clicks=2, interval=0.1)

    @staticmethod
    def _does_char_have_recall_potion():
        return pyag.pixelMatchesColor(664, 725, (120, 151, 154), tolerance=20)

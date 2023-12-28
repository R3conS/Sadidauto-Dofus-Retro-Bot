from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import pyautogui as pyag

from src.bot.map_changer.map_changer import MapChanger
from src.bot.states.out_of_combat.status_enum import Status


class Handler:

    _ASTRUB_BANK_MAP = "4,-16"
    _ASTRUB_ZAAP_MAP = "4,-19"
    _NO_RECALL_MAPS = ["4,-16", "4,-17", "4,-18", "4,-19"]

    @classmethod
    def handle(cls):
        if cls._recall() == Status.FAILED_TO_DETECT_LOADING_SCREEN_AFTER_RECALL:
            return Status.FAILED_TO_RECALL
        if cls._run_to_bank() == Status.ARRIVED_AT_ASTRUB_BANK_MAP:
            return Status.ARRIVED_AT_ASTRUB_BANK_MAP

    @classmethod
    def _recall(cls):
        if not cls._is_char_on_no_recall_map():
            log.info("Character is not on a no-recall map. Attempting to recall ... ")
            if cls._does_char_have_recall_potion():
                cls._use_recall_potion()
                if MapChanger.has_loading_screen_passed():
                    if MapChanger.get_current_map_coords() == cls._ASTRUB_ZAAP_MAP:
                        log.info("Successfully recalled.")
                        return Status.SUCCESSFULLY_RECALLED
                else:
                    log.error("Failed to detect loading screen after recalling.")
                    return Status.FAILED_TO_DETECT_LOADING_SCREEN_AFTER_RECALL
            else:
                log.info("Character does not have a recall potion.")
                return Status.CHAR_DOESNT_HAVE_RECALL_POTION
        else:
            log.info("Character is close to the bank. No need to recall.")
            return Status.NO_NEED_TO_RECALL

    @classmethod
    def _run_to_bank(cls):
        path_to_bank = MapChanger.get_shortest_path(MapChanger.get_current_map_coords(), cls._ASTRUB_BANK_MAP)
        while True:
            map_coords = MapChanger.get_current_map_coords()
            if map_coords == cls._ASTRUB_BANK_MAP:
                log.info("Arrived at Astrub bank map.")
                return Status.ARRIVED_AT_ASTRUB_BANK_MAP

            log.info(f"Running to bank. Current map coords: {map_coords}.")
            MapChanger.change_map(map_coords, path_to_bank[map_coords])
            if MapChanger.has_loading_screen_passed():
                continue
            log.error("Failed to detect loading screen after changing map.")
            return Status.FAILED_TO_DETECT_LOADING_SCREEN_AFTER_CHANGE_MAP

    @classmethod
    def _is_char_on_no_recall_map(cls):
        return MapChanger.get_current_map_coords() in cls._NO_RECALL_MAPS

    @staticmethod
    def _use_recall_potion():
        pyag.moveTo(664, 725)
        pyag.click(clicks=2, interval=0.1)

    @staticmethod
    def _does_char_have_recall_potion():
        return pyag.pixelMatchesColor(664, 725, (120, 151, 154), tolerance=20)

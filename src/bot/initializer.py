from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import os

import pygetwindow as gw

from src.bot.interfaces.interfaces import Interfaces
from screen_capture import ScreenCapture
from src.ocr.ocr import OCR


class Initializer:

    WINDOW_TITLE = None
    _WINDOW_SUFFIXES = ["Dofus Retro", "Abrak"]
    _WINDOW_SIZE = (950, 785)
    _WINDOW_POS = (-8, 0)
    _VALID_SCRIPTS = [
        "af_anticlock", 
        "af_clockwise"
    ]

    def __init__(self, script: str, character_name: str):
        self._script = script
        self._character_name = character_name
        if not self._is_script_valid(self._script):
            log.critical(f"Invalid script name '{self._script}'! Exiting ... ")
            os._exit(1)
        self._prepare_game_window()
        self._verify_character_name()

    def _is_script_valid(self, script_to_check):
        for script in self._VALID_SCRIPTS:
            if script == script_to_check:
                return True
        return False

    def _prepare_game_window(self):
        log.info("Attempting to prepare Dofus window ... ")
        if bool(gw.getWindowsWithTitle(self._character_name)):
            for w in gw.getWindowsWithTitle(self._character_name):
                if any(suffix in w.title for suffix in self._WINDOW_SUFFIXES):
                    w.restore()
                    w.activate()
                    w.resizeTo(*self._WINDOW_SIZE)
                    w.moveTo(*self._WINDOW_POS)
                    log.info(f"Successfully prepared '{w.title}' Dofus window!")
                    self.WINDOW_TITLE = w.title
                    return
        log.critical(f"Failed to detect Dofus window for '{self._character_name}'! Exiting ...")
        os._exit(1)

    def _verify_character_name(self):
        log.info("Verifying character's name ... ")
        Interfaces.open_characteristics()
        if Interfaces.is_characteristics_open():
            sc = ScreenCapture.custom_area((685, 93, 205, 26))
            if self._character_name == OCR.get_text_from_image(sc):
                log.info("Successfully verified character's name!")
                Interfaces.close_characteristics()
                if not Interfaces.is_characteristics_open():
                    return
            else:
                log.critical("Invalid character name! Exiting ... ")
                os._exit(1)
        else:
            log.critical(
                "Failed to verify character's name because 'Characteristics' "
                "interface is not open! Exiting ... "
            )
            os._exit(1)

from src.logger import Logger
log = Logger.get_logger(Logger.DEBUG, True, True)

import os

import pygetwindow as gw
import ctypes

from src.utilities.screen_capture import ScreenCapture
from src.utilities.ocr.ocr import OCR
from src.bot._interfaces.interfaces import Interfaces
from src.bot._initializer._disturbance_checker import DisturbanceChecker


class Initializer:

    WINDOW_SUFFIXES = ["Dofus Retro", "Abrak"]
    WINDOW_SIZE = (950, 785)
    WINDOW_POS = (-8, 0)
    VALID_SCRIPTS = [
        "af_anticlock", 
        "af_clockwise"
    ]
    VALID_SERVERS = [
        "Boune",
        "Allisteria",
        "Fallanster",
        "Semi-like" # Abrak.
    ]

    def __init__(self, script: str, character_name: str, server_name: str):
        self._script = script
        self._character_name = character_name
        self._server_name = server_name
        self._disturbance_checker = DisturbanceChecker()
        self.character_level = None
        self.window_title = None
        self.window_hwnd = None

    def initialize(self):
        log.info("Initializing bot ...")
        self._verify_script()
        self._verify_server()
        self._prepare_game_window()
        self._verify_character_name()
        self.character_level = self._read_character_level()
        self._start_disturbance_checker()
        log.info("Successfully initialized bot!")

    def _verify_script(self):
        log.info("Verifying script ...")
        if self._script not in self.VALID_SCRIPTS:
            log.critical(f"Script name is invalid: '{self._script}'! Exiting ... ")
            os._exit(1)
        log.info(f"Successfully verified script!")

    def _verify_server(self):
        log.info("Verifying server ...")
        if self._server_name not in self.VALID_SERVERS:
            log.critical(f"Server name is invalid: '{self._server_name}'! Exiting ... ")
            os._exit(1)
        log.info(f"Successfully verified server!")

    def _prepare_game_window(self):
        log.info("Preparing Dofus window ...")
        if bool(gw.getWindowsWithTitle(self._character_name)):
            for w in gw.getWindowsWithTitle(self._character_name):
                if any(suffix in w.title for suffix in self.WINDOW_SUFFIXES):
                    ctypes.windll.user32.SetWindowPos( # Set window to topmost/always on top.
                        w._hWnd, 
                        ctypes.wintypes.HWND(-1), 
                        0, 0, 0, 0, 
                        0x0002 | 0x0001
                    )
                    w.restore()
                    w.activate()
                    w.resizeTo(*self.WINDOW_SIZE)
                    w.moveTo(*self.WINDOW_POS)
                    self.window_title = w.title
                    self.window_hwnd = w._hWnd
                    log.info(f"Successfully prepared '{w.title}' Dofus window!")
                    return
        log.critical(f"Failed to detect Dofus window for '{self._character_name}'! Exiting ...")
        os._exit(1)

    def _verify_character_name(self):
        log.info("Verifying character's name ... ")
        Interfaces.CHARACTERISTICS.open()
        sc = ScreenCapture.custom_area((685, 93, 205, 26))
        text = OCR.get_text_from_image(sc)
        if self._character_name == text:
            log.info("Successfully verified character's name!")
            Interfaces.CHARACTERISTICS.close()
        else:
            log.critical(
                f"Provided character's name '{self._character_name}' does not "
                f"match the one in-game '{text}'! Exiting ..."
            )
            os._exit(1)

    @staticmethod
    def _read_character_level():
        log.info("Reading character's level ... ")
        Interfaces.CHARACTERISTICS.open()
        sc = ScreenCapture.custom_area((735, 129, 39, 21))
        level = OCR.get_text_from_image(sc)
        if level.isdigit():
            log.info(f"Successfully read character's level: {level}!")
            Interfaces.CHARACTERISTICS.close()
            return int(level)
        log.critical(f"Failed to read character's level! Exiting ...")
        os._exit(1)

    def _start_disturbance_checker(self):
        log.info("Starting disturbance checker ... ")
        self._disturbance_checker.start()
        log.info("Successfully started disturbance checker!")


if __name__ == "__main__":
    initializer = Initializer("af_clockwise", "Juni", "Semi-like")
    initializer.initialize()

from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import os

import pygetwindow as gw

from image_detection import ImageDetection
from interfaces import Interfaces
from state.botstate_enum import BotState
from screen_capture import ScreenCapture
from src.ocr.ocr import OCR


class Initializer:

    __window_suffixes = ["Dofus Retro", "Abrak"]
    window_size = (950, 785)
    window_title = None
    __window_pos = (-8, 0)
    __valid_scripts = [
        "af_anticlock", 
        "af_clockwise", 
        "af_north", 
        "af_east", 
        "af_south", 
        "af_west"
    ]

    def __init__(self, script: str, character_name: str, set_bot_state_callback):
        self.__script = script
        self.__character_name = character_name
        self.__set_bot_state_callback = set_bot_state_callback
        if not self.__is_script_valid(self.__script):
            log.critical(f"Invalid script name '{self.__script}'! Exiting ... ")
            os._exit(1)
        self.__prepare_game_window()
        self.__verify_character_name()
        self.__set_initial_bot_state()

    def __is_script_valid(self, script_to_check):
        for script in self.__valid_scripts:
            if script == script_to_check:
                return True
        return False

    def __prepare_game_window(self):
        log.info("Attempting to prepare Dofus window ... ")
        if bool(gw.getWindowsWithTitle(self.__character_name)):
            for w in gw.getWindowsWithTitle(self.__character_name):
                if any(suffix in w.title for suffix in self.__window_suffixes):
                    w.restore()
                    w.activate()
                    w.resizeTo(*self.window_size)
                    w.moveTo(*self.__window_pos)
                    log.info(f"Successfully prepared '{w.title}' Dofus window!")
                    self.window_title = w.title
                    return
        log.critical(f"Failed to detect Dofus window for '{self.__character_name}'! Exiting ...")
        os._exit(1)

    def __verify_character_name(self):
        log.info("Verifying character's name ... ")
        Interfaces.open_characteristics()
        if Interfaces.is_characteristics_open():
            sc = ScreenCapture.custom_area((685, 93, 205, 26))
            if self.__character_name == OCR.get_text_from_image(sc, ocr_engine="paddleocr")[0]:
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

    def __set_initial_bot_state(self):
        image_paths = [
            "src\\initializer\\cc_lit.png",
            "src\\initializer\\cc_dim.png"
        ]
        game_window_image = ScreenCapture.game_window()
        for path in image_paths:
            if len(ImageDetection.find_image(game_window_image, path, 0.98)) > 0:
                self.__set_bot_state_callback(BotState.IN_COMBAT)
                break
        self.__set_bot_state_callback(BotState.OUT_OF_COMBAT)

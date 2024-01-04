from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import os
from time import perf_counter

import cv2
import pyautogui as pyag

from ._turn_detector import TurnDetector
from ._first_turn_handler.handler import Handler as FirstTurnHandler
from ._subsequent_turn_handler.handler import Handler as SubsequentTurnHandler
from src.utilities import load_image
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture
from src.bot._states.in_combat._combat_options.combat_options import CombatOptions
from src.bot._states.in_combat._status_enum import Status
from src.bot._exceptions import RecoverableException


class Fighter:

    IMAGE_FOLDER_PATH = "src\\bot\\_states\\in_combat\\_sub_states\\fighting\\_images"
    CLOSE_BUTTON_IMAGES = [
        load_image(IMAGE_FOLDER_PATH, "close_button.png"),
        load_image(IMAGE_FOLDER_PATH, "close_button_2.png"),
    ]

    def __init__(self, script: str, character_name: str):
        self._script = script
        self._character_name = character_name

    def fight(self):
        while True:
            try:
                if TurnDetector.detect_start_of_turn(self._character_name) == Status.FIGHT_RESULTS_WINDOW_DETECTED:
                    self._close_fight_results_window()
                    return
                
                if TurnDetector.is_first_turn():
                    FirstTurnHandler.handle(self._script, self._character_name)
                else:
                    SubsequentTurnHandler.handle(self._character_name)
                        
                TurnDetector.pass_turn(self._character_name)
                
            except RecoverableException:
                # ToDo: implement recovery code here.
                log.error("Recoverable exception occurred while fighting. Exiting ...")
                os._exit(1)

    @classmethod
    def _close_fight_results_window(cls):
        log.info("Closing 'Fight Results' window ...")
        close_button_pos = cls._get_close_button_pos()
        if close_button_pos is None:
            raise RecoverableException("Close button's position was not found.")
        pyag.moveTo(*close_button_pos)
        pyag.click()

        timeout = 5
        start_time = perf_counter()
        while perf_counter() - start_time <= timeout:
            if not cls._is_close_button_visible():
                log.info("Successfully closed 'Fight Results' window.")
                return Status.SUCCESSFULLY_CLOSED_FIGHT_RESULTS_WINDOW
            
        raise RecoverableException(f"Failed to detect if 'Fight Results' window was closed. Timed out: {timeout} seconds.")

    @classmethod
    def _get_close_button_pos(cls):
        rectangle = ImageDetection.find_images(
            haystack=ScreenCapture.game_window(),
            needles=cls.CLOSE_BUTTON_IMAGES,
            confidence=0.98,
            method=cv2.TM_SQDIFF_NORMED,
        )
        if len(rectangle) <= 0:
            return None
        return ImageDetection.get_rectangle_center_point(rectangle[0])

    @classmethod
    def _is_close_button_visible(cls):
        return len(
            ImageDetection.find_images(
                haystack=ScreenCapture.game_window(),
                needles=cls.CLOSE_BUTTON_IMAGES,
                confidence=0.98,
                method=cv2.TM_SQDIFF_NORMED,
            )
        ) > 0

from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import os
from time import perf_counter

import cv2
import pyautogui as pyag

from src.utilities import load_image
from .data.getter import Getter as FightingDataGetter
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture
from .status_enum import Status
from ._turn_detector import TurnDetector
from ._fight_preferences.tactical_mode import TacticalMode
from ._first_turn_handler.handler import Handler as FirstTurnHandler
from ._subsequent_turn_handler.handler import Handler as SubsequentTurnHandler


class Fighter:

    image_folder_path = "src\\bot\\states\\in_combat\\sub_state\\fighting\\images"
    close_button_image = load_image(image_folder_path, "close_button.png")

    def __init__(self, script: str, character_name: str):
        self.__script = script
        self.__character_name = character_name

    def fight(self):
        is_tactical_mode_enabled = False
        while True:
            result = TurnDetector.detect_start_of_turn(self.__character_name)
            if result == Status.FIGHT_RESULTS_WINDOW_DETECTED:
                result = self._close_fight_results_window()
                if result == Status.FAILED_TO_CLOSE_FIGHT_RESULTS_WINDOW:
                    return Status.FAILED_TO_FINISH_FIGHTING
                return Status.SUCCESSFULLY_FINISHED_FIGHTING
            elif (
                result == Status.LOGIN_SCREEN_DETECTED
                or result == Status.FAILED_TO_DETECT_AP_COUNTER
                or result == Status.TIMED_OUT_WHILE_DETECTING_TURN
            ):
                return Status.FAILED_TO_FINISH_FIGHTING

            if not is_tactical_mode_enabled:
                result = TacticalMode.turn_on()
                if (
                    result == Status.TIMED_OUT_WHILE_SHRINKING_TURN_BAR
                    or result == Status.FAILED_TO_GET_TACTICAL_MODE_TOGGLE_ICON_POS
                    or result == Status.TIMED_OUT_WHILE_TURNING_ON_TACTICAL_MODE
                ):
                    return Status.FAILED_TO_FINISH_FIGHTING
                else:
                    is_tactical_mode_enabled = True

            if TurnDetector.is_first_turn():
                # ToDo: add logic that passes turn if actions successfully handled.
                result = FirstTurnHandler.handle(self.__script, self.__character_name)
                if result == Status.FAILED_TO_HANDLE_FIRST_TURN_ACTIONS:
                    return Status.FAILED_TO_FINISH_FIGHTING
            else:
                # ToDo: add logic that passes turn if actions successfully handled.
                # Maybe connect these two together.
                result = SubsequentTurnHandler.handle(self.__character_name)
                if result == Status.FAILED_TO_HANDLE_SUBSEQUENT_TURN_ACTIONS:
                    return Status.FAILED_TO_FINISH_FIGHTING

            os._exit(0)

    @classmethod
    def _close_fight_results_window(cls):
        if not cls._is_close_button_visible():
            log.error("Failed to close 'Fight Results' window because the close button is not visible.")
            return Status.FAILED_TO_CLOSE_FIGHT_RESULTS_WINDOW

        close_button_pos = cls._get_close_button_pos()
        if close_button_pos is None:
            log.error("Failed to close 'Fight Results' screen because the close button's position was not found.")
            return Status.FAILED_TO_CLOSE_FIGHT_RESULTS_WINDOW
        pyag.moveTo(*close_button_pos)
        pyag.click()

        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if not cls._is_close_button_visible():
                log.info("Successfully closed 'Fight Results' window.")
                return Status.SUCCESSFULLY_CLOSED_FIGHT_RESULTS_WINDOW
        else:
            log.error("Timed out while waiting for 'Fight Results' window to close.")
            return Status.FAILED_TO_CLOSE_FIGHT_RESULTS_WINDOW

    @classmethod
    def _get_close_button_pos(cls):
        rectangle = ImageDetection.find_image(
            haystack=ScreenCapture.game_window(),
            needle=cls.close_button_image,
            confidence=0.98,
            method=cv2.TM_CCOEFF_NORMED
        )
        if len(rectangle) <= 0:
            return None
        return ImageDetection.get_rectangle_center_point(rectangle)

    @classmethod
    def _is_close_button_visible(cls):
        return len(
            ImageDetection.find_image(
                haystack=ScreenCapture.game_window(),
                needle=cls.close_button_image,
                confidence=0.98,
                method=cv2.TM_CCOEFF_NORMED,
            )
        ) > 0

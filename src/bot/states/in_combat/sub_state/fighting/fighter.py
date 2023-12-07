from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import os
from time import perf_counter

import cv2
import pyautogui as pyag

from .data.getter import Getter as FightingDataGetter
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture
from .status_enum import Status
from ._turn_detector import TurnDetector
from ._first_turn_handler.handler import Handler as FirstTurnHandler
from ._fight_preferences.tactical_mode import TacticalMode


class Fighter:

    image_folder_path = "src\\bot\\states\\in_combat\\sub_state\\fighting\\images"

    def __init__(self, script: str, character_name: str):
        self.__script = script
        self.__character_name = character_name

    def fight(self):
        is_tactical_mode_enabled = False
        while True:
            # ToDo: add fight end detection to detect_start_of_turn() method.
            # ToDo: periodically check if logged out while checking for turn.
            # ToDo: also check if orange sand timer is filling up.
            result = TurnDetector.detect_start_of_turn(self.__character_name)
            if result == Status.TIMED_OUT_WHILE_DETECTING_TURN:
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
                result = FirstTurnHandler.handle(self.__script, self.__character_name)
                if result == Status.FAILED_TO_HANDLE_FIRST_TURN_ACTIONS:
                    return Status.FAILED_TO_FINISH_FIGHTING
                
            os._exit(0)

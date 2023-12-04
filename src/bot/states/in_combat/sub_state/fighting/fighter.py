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

    # ToDo: add method to detect red/blue circles if model disabler is off.
    # The icon to turn it off/on disappears after a reconnect.

    image_folder_path = "src\\bot\\states\\in_combat\\sub_state\\fighting\\images"

    def __init__(self, script: str, character_name: str):
        self.__script = script
        self.__character_name = character_name
        fighting_data_getter = FightingDataGetter.get_data_object(script)
        self.__movement_data = fighting_data_getter.get_movement_data()
        self.__spell_casting_data = fighting_data_getter.get_spell_casting_data()
        self.__starting_cells = fighting_data_getter.get_starting_cells()
        self.__first_turn_handler = FirstTurnHandler(script, character_name)

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
                # ToDo: add CharacterMover class that moves character on first turn.
                # Or just handle moving and casting on this handler and create
                # another one for not first turn.
                result = FirstTurnHandler.handle(self.__script, self.__character_name)

            os._exit(0)

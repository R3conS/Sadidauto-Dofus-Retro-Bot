from src.logger import Logger
log = Logger.get_logger()

import ctypes
import os
import threading
import traceback

import pyautogui as pyag
import pygetwindow as gw

from src.bot._disturbance_checker import DisturbanceChecker
from src.bot._exceptions import RecoverableException, UnrecoverableException
from src.bot._interfaces.interfaces import Interfaces
from src.bot._recoverer.recoverer import Recoverer
from src.bot._states.in_combat.controller import Controller as IC_Controller
from src.bot._states.out_of_combat.controller import Controller as OOC_Controller
from src.bot._states.state_determiner.determiner import determine_state
from src.bot._states.states_enum import State
from src.utilities.general import screenshot_game_and_save_to_debug_folder
from src.utilities.ocr.ocr import OCR
from src.utilities.screen_capture import ScreenCapture


class Bot(threading.Thread):
    """Main controller."""

    WINDOW_SUFFIXES = ["Dofus Retro", "Abrak"]
    WINDOW_SIZE = (950, 785)
    WINDOW_POS = (-8, 0)

    def __init__(
        self, 
        character_name: str, 
        server_name: str,
        script: str,
        go_bank_when_pods_percentage: int = 95,
        disable_spec_mode: bool = True
    ):
        super().__init__()
        self.daemon = True
        self._stopped = False
        self._window_title, self._window_hwnd = self._prepare_game_window(character_name)
        self._character_name = self._verify_character_name(character_name)
        self._script = self._parse_script_name(script)
        self._go_bank_when_pods_percentage = go_bank_when_pods_percentage
        self._disable_spec_mode = disable_spec_mode
        self._interfaces = Interfaces(self._script, self._window_title)
        self._out_of_combat_controller = OOC_Controller(self._set_state, self._script, self._window_title)
        self._in_combat_controller = IC_Controller(self._set_state, self._script, self._character_name)
        self._character_level = self._read_character_level()
        self._server_name = server_name
        self._recoverer = Recoverer(
            self._character_name, 
            self._server_name, 
            self._character_level, 
            self._window_hwnd, 
            self.WINDOW_SIZE
        )
        self._recovery_finished_event = threading.Event()
        self._recovery_finished_event.set()
        self._out_of_combat_state_event = threading.Event()
        self._out_of_combat_state_event.set()
        self._has_disturbance_checker_crashed = False
        self._disturbance_checker = DisturbanceChecker(
            self._recovery_finished_event,
            self._out_of_combat_state_event,
            self._set_disturbance_checker_crashed
        )
        self._disturbance_checker.start()
        self._state = determine_state()

    def run(self):
        try:
            while not self._stopped:
                try:
                    if self._has_disturbance_checker_crashed:
                        self._has_disturbance_checker_crashed = False
                        self._restart_disturbance_checker()

                    if self._state == State.OUT_OF_COMBAT:
                        self._out_of_combat_state_event.set()
                        self._out_of_combat_controller.run()
                    elif self._state == State.IN_COMBAT:
                        self._out_of_combat_state_event.clear()
                        self._in_combat_controller.run()
                except RecoverableException as e:
                    self._recovery_finished_event.clear()
                    self._recoverer.recover(e.reason, e.occured_in_sub_state)
                    self._state = determine_state()
                    self._recovery_finished_event.set()
                    continue
        except UnrecoverableException:
            log.critical(traceback.format_exc())
        except Exception:
            log.critical("An unhandled exception occured!")
            log.critical(traceback.format_exc())
            screenshot_game_and_save_to_debug_folder("Bot - UnhandledException")
        finally:
            self._logout()
            log.info("Exiting ... ")
            os._exit(1)

    def stop(self):
        self._stopped = True

    def _set_state(self, state):
        self._state = state

    @staticmethod
    def _logout():
        log.info("Attempting to logout ... ")
        try:
            if not Interfaces.LOGIN_SCREEN.is_open():
                Interfaces.MAIN_MENU.open()
                Interfaces.MAIN_MENU.click_logout()
                if Interfaces.CAUTION.is_open():
                    Interfaces.CAUTION.click_yes()
                if Interfaces.LOGIN_SCREEN.is_open():
                    log.info("Successfully logged out!")
                    return
            else:
                log.info("Already logged out!")
        except Exception:
            log.critical("An exception occured while attempting to logout!")
            log.critical(traceback.format_exc())
            screenshot_game_and_save_to_debug_folder("failed_to_logout")
            log.critical("Closing Dofus window ... ")
            cross_button_pos = Interfaces.MAIN_MENU.get_cross_button_pos()
            if cross_button_pos is not None:
                pyag.moveTo(cross_button_pos[0], cross_button_pos[1] - 40)
                pyag.click()

    @classmethod
    def _prepare_game_window(cls, character_name):
        log.info("Preparing Dofus window ...")
        if bool(gw.getWindowsWithTitle(character_name)):
            for w in gw.getWindowsWithTitle(character_name):
                if any(suffix in w.title for suffix in cls.WINDOW_SUFFIXES):
                    ctypes.windll.user32.SetWindowPos( # Set window to topmost/always on top.
                        w._hWnd, 
                        ctypes.wintypes.HWND(-1), 
                        0, 0, 0, 0, 
                        0x0002 | 0x0001
                    )
                    w.restore()
                    w.activate()
                    w.resizeTo(*cls.WINDOW_SIZE)
                    w.moveTo(*cls.WINDOW_POS)
                    log.info(f"Successfully prepared '{w.title}' Dofus window!")
                    return w.title, w._hWnd
        log.critical(f"Failed to detect Dofus window for '{character_name}'! Exiting ...")
        os._exit(1)

    @staticmethod
    def _verify_character_name(character_name):
        log.info("Verifying character's name ... ")
        Interfaces.CHARACTERISTICS.open()
        sc = ScreenCapture.custom_area((685, 93, 205, 26))
        text = OCR.get_text_from_image(sc)
        if character_name == text:
            log.info("Successfully verified character's name!")
            Interfaces.CHARACTERISTICS.close()
            return character_name
        else:
            log.critical(
                f"Provided character's name '{character_name}' does not "
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
        log.critical("Failed to read character's level! Exiting ...")
        os._exit(1)

    def _set_disturbance_checker_crashed(self):
        log.error("'DisturbanceChecker' has crashed!")
        self._has_disturbance_checker_crashed = True

    def _restart_disturbance_checker(self):
        log.info("Restarting 'DisturbanceChecker' ... ")
        self._disturbance_checker = DisturbanceChecker(
            self._recovery_finished_event,
            self._out_of_combat_state_event,
            self._set_disturbance_checker_crashed
        )
        self._disturbance_checker.start()

    @staticmethod
    def _parse_script_name(script: str):
        script = script.lower()
        if "astrub forest" in script:
            if "anticlock" in script:
                return "af_anticlock"
            elif "clockwise" in script:
                return "af_clockwise"
        else:
            log.critical(f"Invalid script name '{script}'! Exiting ...")
            os._exit(1)

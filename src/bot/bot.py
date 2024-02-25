from src.logger import get_logger

log = get_logger()

import ctypes
import multiprocessing as mp
import os
import threading
import traceback

import pyautogui as pyag

from src.bot._disturbance_checker import DisturbanceChecker
from src.bot._exceptions import InitializationException, RecoverableException, UnrecoverableException
from src.bot._interfaces.interfaces import Interfaces
from src.bot._recoverer.recoverer import Recoverer
from src.bot._states.in_combat.controller import Controller as IC_Controller
from src.bot._states.out_of_combat.controller import Controller as OOC_Controller
from src.bot._states.state_determiner.determiner import determine_state
from src.bot._states.states_enum import State
from src.utilities import pygetwindow_custom as gw
from src.utilities.general import screenshot_game_and_save_to_debug_folder
from src.utilities.ocr.ocr import OCR
from src.utilities.screen_capture import ScreenCapture


class Bot(mp.Process):
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
        disable_spectator_mode: bool = True
    ):
        super().__init__()
        self.daemon = True
        self.name = "BotProcess" # Used to set the FileHandler in Logger.
        self._character_name = character_name
        self._server_name = server_name
        self._script = script
        self._go_bank_when_pods_percentage = go_bank_when_pods_percentage
        self._disable_spectator_mode = disable_spectator_mode

    def run(self):
        try:
            self._script = self._verify_script_name(self._script)
            self._verify_server_name(self._server_name)
            self._window_title, self._window_hwnd = self._prepare_game_window(self._character_name)
            self._character_name = self._verify_provided_name_matches_in_game(self._character_name)
            self._interfaces = Interfaces(self._script, self._window_title)
            self._out_of_combat_controller = OOC_Controller(
                self._set_state, 
                self._script, 
                self._window_title,
                self._go_bank_when_pods_percentage
            )
            self._in_combat_controller = IC_Controller(
                self._set_state, 
                self._script, 
                self._character_name,
                self._disable_spectator_mode
            )
            self._character_level = self._read_character_level()
            self._recoverer = Recoverer(
                self._character_name, 
                self._server_name, 
                self._script,
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
            while True:
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
        except InitializationException:
            log.critical("Exiting ... ")
            os._exit(1)
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
        self.terminate()

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

    @staticmethod
    def _verify_script_name(script: str):
        script = script.lower()
        if "astrub forest" in script:
            if "anticlock" in script:
                return "af_anticlock"
            elif "clockwise" in script:
                return "af_clockwise"
        if script == "":
            raise InitializationException("Script name field is empty!")
        raise InitializationException(f"Invalid script name '{script}'!")

    @staticmethod
    def _verify_server_name(server_name: str):
        if server_name.lower() not in ["boune", "allisteria", "fallanster", "semi-like (abrak)"]:
            if server_name == "":
                raise InitializationException("Server name field is empty!")
            raise InitializationException(f"Invalid server name: '{server_name}'!")
        return server_name

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
        raise InitializationException(f"Failed to detect Dofus window with name: '{character_name}'!")

    @staticmethod
    def _verify_provided_name_matches_in_game(character_name):
        try:
            log.info("Verifying character's name ... ")
            Interfaces.CHARACTERISTICS.open()
            sc = ScreenCapture.custom_area((685, 93, 205, 26))
            sc = OCR.resize_image(sc, sc.shape[1] * 2, sc.shape[0] * 2)
            sc = OCR.convert_to_grayscale(sc)
            sc = OCR.invert_image(sc)
            text = OCR.get_text_from_image(sc)
            if character_name == text:
                log.info("Successfully verified character's name!")
                Interfaces.CHARACTERISTICS.close()
                return character_name
            else:
                raise RecoverableException("The provided name and the one in-game do not match!")
        except RecoverableException:
            raise InitializationException("Failed to verify character's name!")

    @staticmethod
    def _read_character_level():
        try:
            log.info("Reading character's level ... ")
            Interfaces.CHARACTERISTICS.open()
            sc = ScreenCapture.custom_area((735, 129, 39, 21))
            level = OCR.get_text_from_image(sc)
            if level.isdigit():
                log.info(f"Successfully read character's level: {level}!")
                Interfaces.CHARACTERISTICS.close()
                return int(level)
            else:
                raise RecoverableException("Read level string is not all digits!")
        except RecoverableException:
            raise InitializationException("Failed to read character's level!")

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

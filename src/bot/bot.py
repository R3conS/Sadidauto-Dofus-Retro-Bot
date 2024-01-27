from src.logger import Logger
log = Logger.get_logger(Logger.DEBUG, True, True)

import glob
import os
import threading
import traceback

import cv2

from src.bot._exceptions import RecoverableException, UnrecoverableException
from src.bot._initializer.initializer import Initializer
from src.bot._recoverer.recoverer import Recoverer
from src.bot._states.in_combat.controller import Controller as IC_Controller
from src.bot._states.out_of_combat.controller import Controller as OOC_Controller
from src.bot._states.states_enum import State
from src.utilities.general import load_image_full_path
from src.utilities.image_detection import ImageDetection
from src.utilities.screen_capture import ScreenCapture


class Bot(threading.Thread):
    """Main bot controller."""

    def __init__(self, script: str, character_name: str, server_name: str):
        super().__init__()
        self.daemon = True
        self._script = script
        self._character_name = character_name
        self._server_name = server_name
        self._state = None
        self._stopped = False
        self._initializer = None
        self._ooc_controller = None
        self._ic_controller = None
        self._recoverer = None

    def run(self):
        try:
            self._initializer = Initializer(
                self._script, 
                self._character_name,
                self._server_name
            )
            self._initializer.initialize()
            self._ooc_controller = OOC_Controller(
                self._set_state, 
                self._script, 
                self._initializer.window_title
            )
            self._ic_controller = IC_Controller(
                self._set_state, 
                self._script, 
                self._character_name
            )
            self._recoverer = Recoverer(
                self._character_name, 
                self._server_name, 
                self._initializer.character_level,
                self._initializer.window_hwnd,
                self._initializer.WINDOW_SIZE
            )
            self._state = self._determine_state()
            while not self._stopped:
                try:
                    if self._state == State.OUT_OF_COMBAT:
                        self._ooc_controller.run()
                    elif self._state == State.IN_COMBAT:
                        self._ic_controller.run()
                except RecoverableException as e:
                    self._recoverer.recover(e.reason, e.occured_in_sub_state)
                    self._state = self._determine_state()
                    continue

        except UnrecoverableException:
            # ToDo: Implement UnrecoverableException class logic.
            # Take screenshots, logout etc.
            log.critical(traceback.format_exc())
            log.critical("Unrecoverable exception occurred! Exiting ...")
            os._exit(1)
        except Exception:
            log.exception("An unhandled exception occured!")
            log.critical("Exiting ... ")
            os._exit(1)

    def stop(self):
        self._stopped = True

    def _set_state(self, state):
        self._state = state

    @staticmethod
    def _determine_state():
        image_folder_path = "src\\bot\\_images\\state_determiner"
        ap_counter_image = load_image_full_path(os.path.join(image_folder_path, "ap_counter_image.png"))
        ready_button_images = [
            load_image_full_path(path) 
            for path in glob.glob(os.path.join(image_folder_path, "ready_button\\*.png"))
        ]
        if (
            len(
                ImageDetection.find_image(
                    haystack=ScreenCapture.custom_area((452, 598, 41, 48)), 
                    needle=ap_counter_image,
                    confidence=0.99,
                    mask=ImageDetection.create_mask(ap_counter_image)
                )
            ) > 0
            or len(
                ImageDetection.find_images(
                    haystack=ScreenCapture.custom_area((678, 507, 258, 91)),
                    needles=ready_button_images,
                    confidence=0.95,
                    method=cv2.TM_CCOEFF_NORMED
                )
            ) > 0
        ):
            log.info(f"Determined bot state: {State.IN_COMBAT}.")
            return State.IN_COMBAT
        log.info(f"Determined bot state: {State.OUT_OF_COMBAT}.")
        return State.OUT_OF_COMBAT

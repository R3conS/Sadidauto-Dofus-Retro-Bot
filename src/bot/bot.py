from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import os
import traceback
import threading

from src.bot._disturbance_checker import DisturbanceChecker
from src.bot._initializer import Initializer
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture
from src.bot._states.out_of_combat.controller import Controller as OOC_Controller
from src.bot._states.in_combat.controller import Controller as IC_Controller
from src.bot._states_enum import States as MainBotStates
from ._exceptions import UnrecoverableException


class Bot(threading.Thread):
    """Main bot controller."""

    def __init__(self, script: str, character_name: str):
        super().__init__()
        self.daemon = True
        self._state = None
        self._stopped = False
        self._disturbance_checker = DisturbanceChecker()
        self._disturbance_checker.start()
        initializer = Initializer(script, character_name)
        self._ooc_controller = OOC_Controller(self.set_state, script, initializer.WINDOW_TITLE)
        self._ic_controller = IC_Controller(self.set_state, script, character_name)

    def run(self):
        try:
            self.determine_state()
            while not self._stopped:
                try:
                    if self._state == MainBotStates.OUT_OF_COMBAT:
                        self._ooc_controller.run()
                    elif self._state == MainBotStates.IN_COMBAT:
                        self._ic_controller.run()
                except UnrecoverableException:
                    log.critical(traceback.format_exc())
                    log.critical("Unrecoverable exception occurred! Exiting ...")
                    os._exit(1)
        except Exception:
            log.exception("An unhandled exception occured!")
            log.critical("Exiting ... ")
            os._exit(1)

    def stop(self):
        self._stopped = True

    def set_state(self, state):
        self._state = state

    def determine_state(self):
        image_folder = "src\\bot\\_images"
        image_names = ["cc_lit.png", "cc_dim.png"]
        game_window_image = ScreenCapture.game_window()
        for name in image_names:
            path = os.path.join(image_folder, name)
            if not os.path.exists(path):
                raise ValueError(f"Image '{path}' does not exist.")
            if not os.path.isfile(path):
                raise ValueError(f"Path '{path}' is not a file.")
            if len(ImageDetection.find_image(game_window_image, path, 0.98)) > 0:
                self.set_state(MainBotStates.IN_COMBAT)
                return
        self.set_state(MainBotStates.OUT_OF_COMBAT)
        return

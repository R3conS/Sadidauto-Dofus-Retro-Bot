from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import os
import threading

from src.bot.disturbance_checker import DisturbanceChecker
from src.bot.initializer import Initializer
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture
from src.bot.states.out_of_combat.controller import Controller as OOC_Controller
from src.bot.states.in_combat.controller import Controller as IC_Controller
from src.bot.main_states_enum import State as MainBotStates


class Controller(threading.Thread):
    """Main bot controller."""

    def __init__(self, script: str, character_name: str):
        super().__init__()
        self.daemon = True
        self.__state = None
        self.__stopped = False
        self.disturbance_checker = DisturbanceChecker()
        self.disturbance_checker.start()
        initializer = Initializer(script, character_name)
        self.ooc_controller = OOC_Controller(self.set_state, script, initializer.window_title)
        self.ic_controller = IC_Controller(self.set_state, script, character_name)

    def run(self):
        try:
            self.determine_state()
            while not self.__stopped:
                if self.__state == MainBotStates.OUT_OF_COMBAT:
                    self.ooc_controller.run()
                elif self.__state == MainBotStates.IN_COMBAT:
                    self.ic_controller.run()
        except:
            log.exception("An exception occured!")
            log.critical("Exiting ... ")
            os._exit(1)

    def stop(self):
        self.__stopped = True

    def set_state(self, state):
        self.__state = state

    def determine_state(self):
        image_folder = "src\\bot\\main_states_determiner_images"
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

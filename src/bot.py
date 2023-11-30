from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import os
import threading

from disturbance_checker import DisturbanceChecker
from src.initializer.initializer import Initializer
from state.botstate_enum import BotState
from state.out_of_combat.controller import Controller as OOC_Controller
from state.in_combat.controller import Controller as IC_Controller


class Bot(threading.Thread):

    def __init__(self, script: str, character_name: str):
        super().__init__()
        self.daemon = True
        self.__state = None
        self.__stopped = False
        self.disturbance_checker = DisturbanceChecker()
        self.disturbance_checker.start()
        initializer = Initializer(script, character_name, self.set_state)
        self.ooc_controller = OOC_Controller(
            self.set_state, 
            script, 
            initializer.window_title
        )
        self.ic_controller = IC_Controller(self.set_state)

    def run(self):
        try:
            while not self.__stopped:
                if self.__state == BotState.OUT_OF_COMBAT:
                    self.ooc_controller.run()
                elif self.__state == BotState.IN_COMBAT:
                    self.ic_controller.run()
        except:
            log.exception("An exception occured!")
            log.critical("Exiting ... ")
            os._exit(1)

    def stop(self):
        self.__stopped = True

    def set_state(self, state):
        self.__state = state

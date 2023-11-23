from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import threading

from state.botstate_enum import BotState
from state.controller import Controller
from disturbance_checker import DisturbanceChecker
import window_capture as wc


class Bot(threading.Thread):

    def __init__(self, script: str, character_name: str):
        super().__init__()
        self.daemon = True
        self.controller = Controller(script, character_name)
        self.disturbance_checker = DisturbanceChecker()
        self.disturbance_checker.start()
        self.hunting = self.controller.hunting
        self.preparing = self.controller.preparing
        self.fighting = self.controller.fighting
        self.moving = self.controller.moving
        self.banking = self.controller.banking
        self.__stopped = False
        self.__state = BotState.CONTROLLER

    def run(self):
        try:
            while not self.__stopped:
                if self.__state == BotState.CONTROLLER:
                    self.__state = self.controller.controller()
                elif self.__state == BotState.HUNTING:
                    self.__state = self.hunting.hunting()
                elif self.__state == BotState.PREPARING:
                    self.__state = self.preparing.preparing()
                elif self.__state == BotState.FIGHTING:
                    self.__state = self.fighting.fighting()
                elif self.__state == BotState.MOVING:
                    self.__state = self.moving.moving()
                elif self.__state == BotState.BANKING:
                    self.__state = self.banking.banking()
        except:
            log.exception("An exception occured!")
            log.critical("Exiting ... ")
            wc.WindowCapture.on_exit_capture()

    def stop(self):
        self.__stopped = True

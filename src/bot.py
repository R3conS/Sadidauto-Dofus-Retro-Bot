from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True)

import threading

from state.botstate_enum import BotState
from state.initializing import Initializing
from state.controller import Controller
from state.hunting import Hunting
from state.preparing import Preparing
from state.fighting import Fighting
from state.moving import Moving
from state.banking import Banking
import window_capture as wc


class Bot(threading.Thread):

    def __init__(self, script: str, character_name: str):
        super().__init__()
        self.daemon = True
        Initializing().initialize(script, character_name)
        self.__stopped = False
        self.__state = BotState.CONTROLLER

    def run(self):
        try:
            while not self.__stopped:
                if self.__state == BotState.CONTROLLER:
                    self.__state = Controller.controller()
                elif self.__state == BotState.HUNTING:
                    self.__state = Hunting.hunting()
                elif self.__state == BotState.PREPARING:
                    self.__state = Preparing.preparing()
                elif self.__state == BotState.FIGHTING:
                    self.__state = Fighting.fighting()
                elif self.__state == BotState.MOVING:
                    self.__state = Moving.moving()
                elif self.__state == BotState.BANKING:
                    self.__state = Banking.banking()
        except:
            log.exception("An exception occured!")
            log.critical("Exiting ... ")
            wc.WindowCapture.on_exit_capture()

    def stop(self):
        self.__stopped = True

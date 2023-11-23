from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import threading
from time import sleep

from pyautogui import moveTo, click

from interfaces import Interfaces


class DisturbanceChecker(threading.Thread):
    """Detect and ignore offers and invites from other players."""

    def __init__(self):
        super().__init__()
        self.daemon = True
        self.__check_interval = 0.5

    def run(self):
        log.info("Disturbance checker started!")
        while True:
            if Interfaces.is_offer_or_invite_open():
                log.info("Offer or invite from another player detected!")
                self.__ignore_for_session()
                if Interfaces.is_offer_or_invite_closed():
                    log.info("Successfully ignored player!")
            sleep(self.__check_interval)

    def __ignore_for_session(self):
        log.info("Ignoring player ... ")
        moveTo(466, 387)
        click()

from src.logger import Logger
log = Logger.get_logger(Logger.DEBUG, True, True)

import threading
from time import sleep

from src.bot._interfaces.interfaces import Interfaces


class DisturbanceChecker(threading.Thread):

    def __init__(self):
        super().__init__()
        self.daemon = True
        self._check_interval = 0.5

    def run(self):
        log.info("Disturbance checker started!")
        while True:
            if Interfaces.OFFER_OR_INVITE.is_open():
                log.info("Offer or invite from another player detected!")
                Interfaces.OFFER_OR_INVITE.close()
            if Interfaces.INFORMATION.is_open():
                log.info("'Information' interface detected!")
                Interfaces.INFORMATION.close()
            sleep(self._check_interval)

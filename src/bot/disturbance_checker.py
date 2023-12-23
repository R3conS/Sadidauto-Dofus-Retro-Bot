from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import threading
from time import sleep

from src.bot.interfaces import Interfaces


class DisturbanceChecker(threading.Thread):

    def __init__(self):
        super().__init__()
        self.daemon = True
        self._check_interval = 0.5

    def run(self):
        log.info("Disturbance checker started!")
        while True:
            if Interfaces.is_offer_or_invite_open():
                log.info("Offer or invite from another player detected!")
                Interfaces.close_offer_or_invite()
                if Interfaces.is_offer_or_invite_open():
                    # ToDo: Implement this when recovery state is implemented
                    pass
            if Interfaces.is_information_open():
                log.info("'Information' interface detected!")
                Interfaces.close_information()
                if Interfaces.is_information_open():
                    # ToDo: Implement this when recovery state is implemented
                    pass 
            sleep(self._check_interval)

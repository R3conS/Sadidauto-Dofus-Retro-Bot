from src.logger import get_logger

log = get_logger()

import threading
import traceback
from time import sleep

from src.bot._exceptions import RecoverableException, UnrecoverableException
from src.bot._interfaces.interfaces import Interfaces
from src.utilities.general import screenshot_game_and_save_to_debug_folder


class DisturbanceChecker(threading.Thread):
    """Checks for and closes any invites or offers from other players."""

    def __init__(
        self,
        recovery_finished_event: threading.Event,
        out_of_combat_state_event: threading.Event,
        set_crashed_callback: callable
    ):
        super().__init__()
        self.daemon = True
        self._recovery_finished_event = recovery_finished_event
        self._out_of_combat_state_event = out_of_combat_state_event
        self._set_disturbance_checker_crashed_callback = set_crashed_callback

    def run(self):
        log.info("'DisturbanceChecker' thread has started.")
        try:
            while True: 
                try:
                    if not self._recovery_finished_event.is_set():
                        log.info("'DisturbanceChecker' thread is paused because recovery is in progress.")
                        self._recovery_finished_event.wait()
                        log.info("'DisturbanceChecker' thread has resumed.")
                    if not self._out_of_combat_state_event.is_set():
                        log.info("'DisturbanceChecker' thread is paused because character is in combat.")
                        self._out_of_combat_state_event.wait()
                        log.info("'DisturbanceChecker' thread has resumed.")

                    if Interfaces.OFFER_OR_INVITE.is_open():
                        log.info("Offer or invite from another player detected!")
                        Interfaces.OFFER_OR_INVITE.close()
                    if Interfaces.INFORMATION.is_open():
                        log.info("'Information' interface detected!")
                        Interfaces.INFORMATION.close()
                except RecoverableException:
                    log.error("Recoverable exception occured in 'DisturbanceChecker' thread.")
                    log.error(traceback.format_exc())
                    continue # Bot thread will handle recovery.
        except UnrecoverableException:
            log.critical(traceback.format_exc())
        except Exception:
            log.critical("An unhandled exception occured!")
            log.critical(traceback.format_exc())   
            screenshot_game_and_save_to_debug_folder("DisturbanceChecker - UnhandledException")
        finally:
            self._set_disturbance_checker_crashed_callback()

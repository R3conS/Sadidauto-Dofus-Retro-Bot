from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from ._sub_states.hunting.hunter import Hunter
from ._sub_states.banking.banker import Banker
from ._status_enum import Status
from src.bot._states_enum import States as MainBotStates


class Controller:

    def __init__(
            self, 
            set_bot_state_callback: callable, 
            script: str,
            game_window_title: str,
        ):
        self._set_main_bot_state_callback = set_bot_state_callback
        self._hunter = Hunter(script, game_window_title)
        self._banker = Banker(script, game_window_title)

    def run(self):
        sub_state = _SubStates.HUNTING
        while True:
            if sub_state == _SubStates.HUNTING:
                status = self._hunter.hunt()
                if status == Status.REACHED_PODS_LIMIT:
                    sub_state = _SubStates.BANKING
                    continue
                elif status == Status.SUCCESSFULLY_FINISHED_HUNTING:
                    self._set_main_bot_state_callback(MainBotStates.IN_COMBAT)
                    return
                elif status == Status.FAILED_TO_FINISH_HUNTING:
                    log.error(f"Failed to finish hunting. Attempting to recover ...")
                    self._set_main_bot_state_callback(MainBotStates.RECOVERY)
                    return

            elif sub_state == _SubStates.BANKING:
                self._banker.bank()
                sub_state = _SubStates.HUNTING
                

class _SubStates:

    HUNTING = "HUNTING"
    BANKING = "BANKING"
    RECOVERY = "RECOVERY"

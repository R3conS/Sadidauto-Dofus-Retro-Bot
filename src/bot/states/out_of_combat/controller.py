from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from src.bot.main_states_enum import State as MainBotStates
from .sub_state.hunting.hunter import Hunter
from .sub_state.banking.banker import Banker
from .sub_state.banking.status_enum import Status as BankerStatus
from .sub_state.hunting.status_enum import Status as HunterStatus


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
                if status == HunterStatus.REACHED_PODS_LIMIT:
                    sub_state = _SubStates.BANKING
                    continue
                elif status == HunterStatus.SUCCESSFULLY_FINISHED_HUNTING:
                    self._set_main_bot_state_callback(MainBotStates.IN_COMBAT)
                    return
                elif status == HunterStatus.FAILED_TO_FINISH_HUNTING:
                    log.error(f"Failed to finish hunting. Attempting to recover ...")
                    self._set_main_bot_state_callback(MainBotStates.RECOVERY)
                    return

            elif sub_state == _SubStates.BANKING:
                status = self._banker.bank()
                if status == BankerStatus.SUCCESSFULLY_FINISHED_BANKING:
                    sub_state = _SubStates.HUNTING
                    continue
                elif status == BankerStatus.FAILED_TO_FINISH_BANKING:
                    log.error(f"Failed to finish banking. Attempting to recover ...")
                    self._set_main_bot_state_callback(MainBotStates.RECOVERY)
                    return
                
            elif sub_state == _SubStates.RECOVERY:
                log.error("'Out of Combat' controller failed to determine its sub state. Attempting to recover ...")
                self._set_main_bot_state_callback(MainBotStates.RECOVERY)
                return


class _SubStates:

    HUNTING = "HUNTING"
    BANKING = "BANKING"
    RECOVERY = "RECOVERY"

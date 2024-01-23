from src.logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from enum import Enum

from ._sub_states.hunting.hunter import Hunter
from ._sub_states.banking.banker import Banker
from ._status_enum import Status
from src.bot._states.states_enum import State as MainBotState


class Controller:

    def __init__(self, set_bot_state_callback: callable, script: str, game_window_title: str):
        self._set_main_bot_state_callback = set_bot_state_callback
        self._hunter = Hunter(script, game_window_title)
        self._banker = Banker(script, game_window_title)

    def run(self):
        sub_state = _SubState.HUNTING
        while True:
            if sub_state == _SubState.HUNTING:
                result = self._hunter.hunt()
                if result == Status.SUCCESSFULLY_ATTACKED_MONSTER:
                    self._set_main_bot_state_callback(MainBotState.IN_COMBAT)
                    return
                elif result == Status.REACHED_PODS_LIMIT:
                    sub_state = _SubState.BANKING
                    continue
            elif sub_state == _SubState.BANKING:
                self._banker.bank()
                sub_state = _SubState.HUNTING


class _SubState(Enum):

    HUNTING = "HUNTING"
    BANKING = "BANKING"

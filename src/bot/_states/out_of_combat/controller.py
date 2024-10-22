from src.logger import get_logger

log = get_logger()

from src.bot._states.out_of_combat._status_enum import Status
from src.bot._states.out_of_combat._sub_states.banking.banker import Banker
from src.bot._states.out_of_combat._sub_states.hunting.hunter import Hunter
from src.bot._states.out_of_combat._sub_states.sub_states_enum import State as SubState
from src.bot._states.states_enum import State as MainBotState


class Controller:

    def __init__(
        self, 
        set_bot_state_callback: callable, 
        script: str, 
        go_bank_when_pods_percentage: int = 90,
    ):
        self._set_main_bot_state_callback = set_bot_state_callback
        self._hunter = Hunter(script, go_bank_when_pods_percentage)
        self._banker = Banker(script)

    def run(self):
        sub_state = SubState.HUNTING
        while True:
            if sub_state == SubState.HUNTING:
                result = self._hunter.hunt()
                if result == Status.SUCCESSFULLY_ATTACKED_MONSTER:
                    self._set_main_bot_state_callback(MainBotState.IN_COMBAT)
                    return
                elif result == Status.REACHED_PODS_LIMIT:
                    sub_state = SubState.BANKING
                    continue
            elif sub_state == SubState.BANKING:
                self._banker.bank()
                sub_state = SubState.HUNTING

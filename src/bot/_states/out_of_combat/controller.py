from src.logger import Logger
log = Logger.get_logger()

from src.bot._states.out_of_combat._status_enum import Status
from src.bot._states.out_of_combat._sub_states.banking.banker import Banker
from src.bot._states.out_of_combat._sub_states.hunting.hunter import Hunter
from src.bot._states.out_of_combat._sub_states.sub_states_enum import State as SubState
from src.bot._states.states_enum import State as MainBotState


class Controller:

    def __init__(self, set_bot_state_callback: callable, script: str, game_window_title: str):
        self._set_main_bot_state_callback = set_bot_state_callback
        self._hunter = Hunter(script, game_window_title)
        self._banker = Banker(script, game_window_title)

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

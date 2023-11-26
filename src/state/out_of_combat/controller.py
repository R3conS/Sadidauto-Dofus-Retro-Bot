from src.state.botstate_enum import BotState
from src.bank import Bank
from .sub_state.hunting.hunter import Hunter
from .sub_state.banking.banking import Banker


class Controller:
    
    __pod_limit = 88

    def __init__(
            self, 
            set_bot_state_callback: callable, 
            script: str,
            game_window_title: str,
            game_window_size: tuple[int, int]
        ):
        self.__set_bot_state_callback = set_bot_state_callback
        self.__hunter = Hunter(
            self.__finished_hunting_callback, 
            script,
            game_window_title,
            game_window_size
        )
        self.__banking = Banker(self.__finished_banking_callback)

    def run(self):
        sub_state = self.__determine_sub_state()
        if sub_state == _SubState.HUNTING:
            self.__hunter.hunt()
        elif sub_state == _SubState.BANKING:
            self.__banking.bank()

    def __determine_sub_state(self):
        if Bank.get_pods_percentage() >= self.__pod_limit:
            return _SubState.BANKING
        return _SubState.HUNTING

    def __finished_hunting_callback(self):
        self.__set_bot_state_callback(BotState.IN_COMBAT)

    def __finished_banking_callback(self):
        self.__set_bot_state_callback(BotState.OUT_OF_COMBAT)


class _SubState:

    HUNTING = "HUNTING"
    BANKING = "BANKING"

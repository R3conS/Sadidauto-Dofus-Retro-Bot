from src.state.botstate_enum import BotState
from src.bank import Bank
from sub_state.hunting.hunter import Hunter
from sub_state.banking import Banking


class Controller:
    
    __pod_limit = 88
    __map_type = None
    __fight_limit = 10 # Before checking pods

    was_map_searched = False
    was_map_changed = False
    map_coords = None
    hunting_map_data = None
    banking_map_data = None
    fight_counter = 0 # True total fights counter is in fighting.py
    is_character_overloaded = False

    def __init__(self, set_bot_state_callback, script: str):
        self.__set_bot_state_callback = set_bot_state_callback
        self.__hunter = Hunter(self.__finished_hunting_callback, script)
        self.__banking = Banking(self.__finished_banking_callback)

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

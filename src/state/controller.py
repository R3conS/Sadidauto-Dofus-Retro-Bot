from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import os

import bank
import data

import window_capture as wc
from state.botstate_enum import BotState
from state.hunting import Hunting
from state.preparing import Preparing
from state.fighting import Fighting
from state.moving import MapChanger
from state.banking import Banking


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

    def __init__(self):
        if not self.__is_script_valid(self.__script):
            log.critical(f"Invalid script name '{self.__script}'! Exiting ... ")
            os._exit(1)
        self.__initialize_states()
        self.__load_map_data()

    def controller(self):
        if self.is_character_overloaded:
            return self.__overloaded()
        if self.fight_counter % self.__fight_limit == 0 and self.fight_counter != 0:
            if self.__is_over_pods_limit():
                self.set_overloaded(True)
                log.info("Character is overloaded!")
                return self.__overloaded()
        log.info("Character is not overloaded! Continuing ... ")
        return self.__not_overloaded()

    def set_overloaded(self, is_overloaded):
        self.is_character_overloaded = is_overloaded

    def set_was_map_searched(self, was_map_searched):
        self.was_map_searched = was_map_searched

    def set_was_map_changed(self, was_map_changed):
        self.was_map_changed = was_map_changed

    def __initialize_states(self):
        self.hunting = Hunting(self)
        self.preparing = Preparing(self)
        self.fighting = Fighting(self)
        self.moving = MapChanger(self)
        self.banking = Banking(self)

    def __load_map_data(self):
        self.hunting_map_data = data.scripts.astrub_forest.Hunting.map_data[self.__script]
        self.banking_map_data = data.scripts.astrub_forest.Banking.map_data

    def __overloaded(self):
        self.__load_map_data_to_states(self.banking_map_data)
        self.__load_map_coords_to_states(self.moving.get_coordinates(self.banking_map_data))
        return BotState.BANKING

    # ToDo: Refactor this later
    def __not_overloaded(self):
        if self.was_map_changed or self.map_coords is None:
            self.__load_map_data_to_states(self.hunting_map_data)
            self.map_coords = self.moving.get_coordinates(self.hunting_map_data)
            self.__load_map_coords_to_states(self.map_coords)
            self.__map_type = self.moving.get_map_type(self.hunting_map_data, self.map_coords)
            self.was_map_changed = False

        if self.__map_type == "fightable":
            if not self.was_map_searched:
                return BotState.HUNTING
            elif self.was_map_searched:
                return BotState.MOVING
        elif self.__map_type == "traversable":
            return BotState.MOVING
        else:
            log.critical(f"Invalid map type '{self.__map_type}' for map "
                         f"'{self.map_coords}'! Exiting ... ")
            wc.WindowCapture.on_exit_capture()

    def __is_over_pods_limit(self):
        log.info("Checking if character is overloaded ... ")
        return bank.Bank.get_pods_percentage() >= self.__pod_limit

    def __load_map_data_to_states(self, data):
        self.banking.data_map = data
        self.fighting.data_map = data
        self.moving.data_map = data
        self.preparing.data_map = data

    def __load_map_coords_to_states(self, data):
        self.banking.map_coords = data
        self.fighting.map_coords = data
        self.moving.map_coords = data
        self.preparing.map_coords = data
        self.hunting.map_coords = data

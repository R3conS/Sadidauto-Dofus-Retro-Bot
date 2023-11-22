from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import os

import pygetwindow as gw

import bank
import window_capture as wc
from pop_up import PopUp
import data
import detection as dtc

from state.botstate_enum import BotState
from state.hunting import Hunting
from state.preparing import Preparing
from state.fighting import Fighting
from state.moving import Moving
from state.banking import Banking


class Controller:

    __window_suffixes = ["Dofus Retro", "Abrak"]
    __window_size = (950, 785)
    __window_pos = (-8, 0)
    __valid_scripts = [
        "af_anticlock", 
        "af_clockwise", 
        "af_north", 
        "af_east", 
        "af_south", 
        "af_west"
    ]
    __pod_limit = 88
    __map_type = None
    __fight_limit = 10 # Before checking pods

    map_searched = False
    map_changed = False
    map_coords = None
    data_map = None
    hunting_map_data = None
    banking_map_data = None
    fight_counter = 0

    def __init__(self, script: str, character_name: str):
        self.__script = script
        self.character_name = character_name
        if not self.__is_script_valid(self.__script):
            log.critical(f"Invalid script name '{self.__script}'! Exiting ... ")
            os._exit(1)
        self.__prepare_game_window()
        self.__verify_character_name()
        self.__initialize_states()
        self.__set_script_map_data()

    def controller(self):
        if self.fight_counter % self.__fight_limit == 0 and self.__is_overloaded():
            log.info("Character is overloaded! Switching to 'BANKING' state ... ")
            return self.__overloaded()
        log.info("Character is not overloaded! Continuing ... ")
        return self.__not_overloaded()

    def __is_script_valid(self, script_to_check):
        for script in self.__valid_scripts:
            if script == script_to_check:
                return True
        return False

    def __prepare_game_window(self):
        log.info("Attempting to prepare Dofus window ... ")
        if bool(gw.getWindowsWithTitle(self.character_name)):
            for w in gw.getWindowsWithTitle(self.character_name):
                if any(suffix in w.title for suffix in self.__window_suffixes):
                    w.restore()
                    w.activate()
                    w.resizeTo(*self.__window_size)
                    w.moveTo(*self.__window_pos)
                    log.info(f"Successfully prepared '{w.title}' Dofus window!")
                    return
        log.critical(f"Failed to detect Dofus window for '{self.character_name}'! Exiting ...")
        os._exit(1)

    def __verify_character_name(self):
        log.info("Verifying character's name ... ")
        attempts_allowed = 3
        attempts_total = 0
        while attempts_total < attempts_allowed:
            PopUp.deal()
            if PopUp.interface("characteristics", "open"):
                sc = wc.WindowCapture.custom_area_capture((685, 93, 205, 26))
                r_and_t, _, _ = dtc.Detection.detect_text_from_image(sc)
                if self.character_name == r_and_t[0][1]:
                    PopUp.interface("characteristics", "close")
                    return True
                else:
                    log.critical("Invalid character name! Exiting ... ")
                    os._exit(1)
            else:
                attempts_total += 1
        else:
            log.critical(
                f"Failed to open characteristics interface {attempts_allowed} times!"
                "Exiting ..."
            )
            wc.WindowCapture.on_exit_capture()

    def __initialize_states(self):
        self.hunting = Hunting(self)
        self.preparing = Preparing(self)
        self.fighting = Fighting(self)
        self.moving = Moving(self)
        self.banking = Banking(self)

    def __set_script_map_data(self):
        self.hunting_map_data = data.scripts.astrub_forest.Hunting.map_data[self.__script]
        self.banking_map_data = data.scripts.astrub_forest.Banking.map_data

    def __overloaded(self):
        self.fight_counter += 1 # To avoid checking pods each map when running to bank
        self.__load_data_map(self.banking_map_data)
        self.__load_map_coords(self.moving.get_coordinates(self.banking_map_data))
        return BotState.BANKING

    def __not_overloaded(self):
        if self.map_changed or self.map_coords is None:
            self.__load_data_map(self.hunting_map_data)
            self.map_coords = self.moving.get_coordinates(self.hunting_map_data)
            self.__load_map_coords(self.map_coords)
            self.__map_type = self.moving.get_map_type(self.hunting_map_data, self.map_coords)
            self.map_changed = False

        if self.__map_type == "fightable":
            if self.map_searched == False:
                return BotState.HUNTING
            elif self.map_searched == True:
                return BotState.MOVING
        elif self.__map_type == "traversable":
            return BotState.MOVING
        else:
            log.critical(f"Invalid map type '{self.__map_type}' for map "
                         f"'{self.map_coords}'! Exiting ... ")
            wc.WindowCapture.on_exit_capture()

    def __is_overloaded(self):
        log.info("Checking if character is overloaded ... ")
        return bank.Bank.get_pods_percentage() >= self.__pod_limit

    def __load_data_map(self, data):
        self.banking.data_map = data
        self.fighting.data_map = data
        self.moving.data_map = data
        self.preparing.data_map = data

    def __load_map_coords(self, data):
        self.banking.map_coords = data
        self.fighting.map_coords = data
        self.moving.map_coords = data
        self.preparing.map_coords = data
        self.hunting.map_coords = data

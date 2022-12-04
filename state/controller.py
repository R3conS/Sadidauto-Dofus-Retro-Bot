"""Logic related to 'CONTROLLER' bot state."""

from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True)

from .botstate_enum import BotState
import bank
import pop_up as pu
import state
import window_capture as wc


class Controller:
    """Holds various 'CONTROLLER' state methods."""

    # Public class attributes.
    map_searched = False
    map_changed = False
    map_coords = None
    data_map = None
    data_hunting = None
    data_banking = None
    official_version = None
    fight_counter = 0

    # Private class attributes.
    __state = None
    __character_overloaded = None
    __pod_limit = 90
    __map_type = None

    @classmethod
    def controller(cls):
        """'CONTROLLER' state logic."""
        if cls.official_version:
            cls.__get_group_status()

        if cls.fight_counter % 6 == 0:
            cls.__character_overloaded = cls.__get_pod_status()

        if cls.__character_overloaded:
            cls.__state = cls.__overloaded()
            return cls.__state

        elif not cls.__character_overloaded:
            cls.__state = cls.__not_overloaded()
            return cls.__state

    @classmethod
    def __overloaded(cls):
        """Execute this code when character is overloaded."""
        cls.data_map = cls.data_banking
        cls.__load_data_map(cls.data_map)
        cls.map_coords = state.Moving.get_coordinates(cls.data_map)
        cls.__load_map_coords(cls.map_coords)
        botstate = BotState.BANKING
        return botstate

    @classmethod
    def __not_overloaded(cls):
        """Execute this code when character is not overloaded."""
        if cls.map_changed or cls.map_coords is None:
            cls.data_map = cls.data_hunting
            cls.__load_data_map(cls.data_map)
            cls.map_coords = state.Moving.get_coordinates(cls.data_map)
            cls.__load_map_coords(cls.map_coords)
            cls.__map_type = state.Moving.get_map_type(cls.data_map,
                                                       cls.map_coords)
            cls.map_changed = False

        if cls.__map_type == "fightable":

            if cls.map_searched == False:
                botstate = BotState.HUNTING
                return botstate

            elif cls.map_searched == True:
                botstate = BotState.MOVING
                return botstate

        elif cls.__map_type == "traversable":
            botstate = BotState.MOVING
            return botstate

        else:
            log.critical(f"Invalid map type '{cls.__map_type}' for map "
                         f"'{cls.map_coords}'!")
            log.critical(f"Exiting ... ")
            wc.WindowCapture.on_exit_capture()

    @classmethod
    def __get_pod_status(cls):
        """Check if character is overlaoded or not."""
        # Incrementing by '1' instantly so bot doesn't check pods
        # everytime 'controller()' is called.
        cls.fight_counter += 1
        # Getting pods percentage.
        pods_percentage = bank.Bank.get_pods_percentage()

        if pods_percentage >= cls.__pod_limit:
            log.info("Overloaded! Going to bank ... ")
            overloaded = True
        else:
            log.info("Not overloaded!")
            overloaded = False

        return overloaded

    @staticmethod
    def __get_group_status():
        """Check if character is in group."""
        pu.PopUp.close_right_click_menu()
        if not state.Initializing.in_group():
            log.critical("Character is not in group!")
            log.critical("Exiting ... ")
            wc.WindowCapture.on_exit_capture()

    @staticmethod
    def __load_data_map(data):
        """Load map data to other bot states."""
        state.Banking.data_map = data
        state.Fighting.data_map = data
        state.Moving.data_map = data
        state.Preparing.data_map = data

    @staticmethod
    def __load_map_coords(data):
        """Load map coords to other bot states."""
        state.Banking.map_coords = data
        state.Fighting.map_coords = data
        state.Moving.map_coords = data
        state.Preparing.map_coords = data
        state.Hunting.map_coords = data

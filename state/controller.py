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
    map_coords = None
    data_map = None
    data_hunting = None
    data_banking = None
    data_monsters = None
    official_version = None
    fight_counter = 0

    # Private class attributes.
    __state = None
    __pod_limit = 90

    @classmethod
    def controller(cls):
        """Set bot state according to situation."""
        if cls.official_version:
            pu.PopUp.close_right_click_menu()
            if not state.Initializing.in_group():
                log.critical("Character is not in group!")
                log.critical("Exiting ... ")
                wc.WindowCapture.on_exit_capture()

        if cls.fight_counter % 6 == 0:
            # Incrementing by '1' instantly so bot doesn't check pods
            # everytime 'controller()' is called.
            cls.fight_counter += 1
            # Getting pods percentage.
            pods_percentage = bank.Bank.get_pods_percentage()

            if pods_percentage >= cls.__pod_limit:
                log.info("Overloaded! Going to bank ... ")
                cls.__character_overloaded = True
            else:
                log.info("Not overloaded!")
                cls.__character_overloaded = False

        if cls.__character_overloaded:
            cls.data_map = cls.data_banking
            cls.map_coords = state.Moving.get_coordinates(cls.data_map)
            cls.__state = BotState.BANKING
            return cls.__state

        elif not cls.__character_overloaded:
            cls.data_map = cls.data_hunting
            cls.map_coords = state.Moving.get_coordinates(cls.data_map)
            map_type = state.Moving.get_map_type(cls.data_map, cls.map_coords)

            if map_type == "fightable":

                if cls.map_searched == False:
                    cls.__state = BotState.HUNTING
                    return cls.__state

                elif cls.map_searched == True:
                    cls.__state = BotState.MOVING
                    return cls.__state

            elif map_type == "traversable":
                cls.__state = BotState.MOVING
                return cls.__state

            else:
                log.critical(f"Invalid map type '{map_type}' for map "
                             f"'{cls.map_coords}'!")
                log.critical(f"Exiting ... ")
                wc.WindowCapture.on_exit_capture()

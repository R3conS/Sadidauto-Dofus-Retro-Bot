from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import time

import pyautogui as pyag

from .botstate_enum import BotState
import combat as cbt
import data
import detection as dtc
from interfaces import Interfaces
import window_capture as wc


class Fighting:

    map_coords = None
    data_map = None
    cell_coords = None
    cell_color = None
    cell_select_failed = False

    __state = None
    __failed_to_move = False
    __total_fights = 0

    def __init__(self, controller):
        self.__controller = controller
        cbt.Combat.data_spell_cast = data.scripts.astrub_forest.Cast.data
        cbt.Combat.data_movement = data.scripts.astrub_forest.Movement.data
        cbt.Combat.character_name = self.__controller.character_name

    def fighting(self):
        """'FIGHTING' state logic."""
        first_turn = True
        tbar_shrunk = False
        character_moved = False
        models_hidden = False
        start_time = time.time()
        timeout = 420

        while time.time() - start_time < timeout:

            if cbt.Combat.turn_detect_start():

                if not tbar_shrunk:
                    if cbt.Combat.shrink_turn_bar():
                        tbar_shrunk = True

                if not models_hidden:
                    if cbt.Combat.hide_models():
                        models_hidden = True

                if not character_moved:
                    if self.__move_character():
                        character_moved = True

                if character_moved and first_turn:
                    if self.__cast_spells(first_turn=True):
                        if cbt.Combat.turn_pass():
                            log.info("Waiting for turn ... ")
                            first_turn = False
                            continue

                elif character_moved and not first_turn:
                    if self.__cast_spells(first_turn=False):
                        if cbt.Combat.turn_pass():
                            log.info("Waiting for turn ... ")
                            continue

            elif self.__detect_end_of_fight():
                self.__controller.fight_counter += 1
                self.__total_fights += 1
                self.__state = BotState.CONTROLLER
                log.info(f"Total fights: {self.__total_fights} ... ")
                return self.__state

        else:
            log.critical(f"Failed to complete fight actions in {timeout} "
                         "seconds!")
            log.critical("Timed out!")
            log.critical("Exiting ... ")
            wc.WindowCapture.on_exit_capture()

    def __move_character(self):
        """Move character."""
        attempts = 0
        attempts_allowed = 3

        while attempts < attempts_allowed:

            if self.cell_select_failed:
                log.debug("Getting cell coords and color in 'fighting' ... ")
                # Giving time for 'Illustration to signal your turn' 
                # to disappear.
                time.sleep(3)
                self.cell_coords, self.cell_color = \
                    self.__get_cell_coords_and_color(
                            self.data_map,
                            self.map_coords
                        )
                self.cell_select_failed = False

            move_coords = cbt.Combat.get_movement_coordinates(
                    self.map_coords,
                    self.cell_color,
                    self.cell_coords,
                )

            if cbt.Combat.get_if_char_on_correct_cell(move_coords):
                log.info("Character is standing on correct cell!")
                # MapChanger mouse cursor off character so that spell bar
                # is visible and ready for detection.
                pyag.moveTo(x=609, y=752)
                return True

            else:
                log.info("MapChanger character ... ")
                cbt.Combat.move_character(move_coords)

                start_time = time.time()
                wait_time = 3

                while time.time() - start_time < wait_time:
                    if cbt.Combat.get_if_char_on_correct_cell(move_coords):
                        pyag.moveTo(x=609, y=752)
                        return True
                else:
                    attempts += 1

        else:
            self.__failed_to_move = True
            log.error(f"Failed to move character in {attempts} attempts!")
            log.debug(f"'self.__failed_to_move' = {self.__failed_to_move}")
            return True

    def __cast_spells(self, first_turn):
        """
        Cast spells.
        
        Parameters
        ----------    
        first_turn : bool
            Whether it's the first turn of combat or not.
        
        """
        # Prevents getting cast coordinates on every attempt to cast
        # spell. If omitted, 'get_char_position()' might return false
        # results on 'Ascalion' server, because sometimes after casting 
        # a spell the orange 'cast range' area stays around the 
        # character (Ascalion's bug) and it messes up detection.
        get_char_pos = True
        # Keeps count of how many times spells were cast.
        cast_times = 0
        # Loop control variables.
        start_time = time.time()
        timeout = 30

        while time.time() - start_time < timeout:

            available_spells = cbt.Combat.get_available_spells()

            if len(available_spells) <= 0:
                log.info("No spells available!")
                self.__failed_to_move = False
                return True

            if cast_times >= 2:
                log.debug(f"Setting first turn to 'False' due to too many "
                          "failed attempts to cast spells ... ")
                first_turn = False
                get_char_pos = True
                cast_times = 0

            for spell in available_spells:
  
                spell_coords = cbt.Combat.get_spell_coordinates(spell)
                
                if spell_coords is None:
                    log.debug(f"Spell coords: {spell_coords}")
                    log.debug("Breaking out of 'for' loop!")
                    break

                if first_turn:
                    if self.__failed_to_move and get_char_pos:
                        log.debug(f"Getting 'cast_coords' after failing "
                                  "to move ... ")
                        cast_coords = cbt.Combat.get_char_position()
                        if cast_coords is None:
                            log.debug(f"cast_coords={cast_coords} ... ")
                            log.debug("Continuing ... ")
                            continue
                        else:
                            get_char_pos = False
                    
                    elif not self.__failed_to_move:
                        cast_coords = cbt.Combat.get_spell_cast_coordinates(
                                spell,
                                self.map_coords,
                                self.cell_color,
                                self.cell_coords
                            )

                elif not first_turn and get_char_pos:
                    cast_coords = cbt.Combat.get_char_position()
                    if cast_coords is None:
                        log.debug(f"cast_coords={cast_coords} ... ")
                        log.debug("Continuing ... ")
                        continue
                    else:
                        get_char_pos = False

                if cbt.Combat.cast_spell(spell, spell_coords, cast_coords):
                    break
                else:
                    cast_times += 1
                    break 

        else:
            log.critical(f"Failed to cast spells in {timeout} seconds!")
            log.critical("Exiting ... ")
            wc.WindowCapture.on_exit_capture()

    def __detect_end_of_fight(self):
        """
        Detect 'Fight Results' window and close it.
        
        Returns
        ----------
        True : bool
            If window was successfully closed.
        False : bool
            If 'Fight Results' window couldn't be detected.
        NoReturn
            Exits program if 'Fight Results' window couldn't be closed
            within 'timeout_time' seconds.

        """
        while True:

            # Detecting 'Fight Results' window.
            close_button = self.__detect_results_window()

            if len(close_button) <= 0:
                return False

            elif len(close_button) > 0:

                log.info("Combat has ended!")
                start_time = time.time()
                timeout_time = 60

                while time.time() - start_time < timeout_time:

                    # Closing 'Fight Results' window.
                    close_button = self.__detect_results_window()
                    
                    if len(close_button) <= 0:
                        log.info("Successfully closed 'Fight Results' "
                                 "window!")
                        return True
                    else:
                        log.info("Closing 'Fight Results' window ... ")
                        pyag.moveTo(close_button[0][0],
                                    close_button[0][1],
                                    duration=0.15)
                        pyag.click()
                        # MapChanger mouse off the 'Close' button in case it 
                        # needs to be detected again.
                        pyag.move(100, 0)

                else:
                    log.critical("Couldn't close 'Fight Results' window in "
                                 f"{timeout_time} second(s)!")
                    log.critical("Timed out!")
                    log.critical("Exiting ... ")
                    wc.WindowCapture.on_exit_capture()

    @staticmethod
    def __detect_results_window():
        """
        Detect close button of 'Fight Results' window.

        Returns
        ----------
        close_button : list[Tuple[int, int]]
            `list` of `tuple` containing [(x, y)] coordinates.

        """
        screenshot = wc.WindowCapture.gamewindow_capture()
        close_button = dtc.Detection.get_click_coords(
                dtc.Detection.find(
                        screenshot,
                        data.images.Status.end_of_combat_v_1,
                        threshold=0.75
                    )
                )

        return close_button

    def __get_cell_coords_and_color(self, database, map_coords):
        """
        Get starting cell color and coords.

        Only used when usual logic of starting cell selection fails
        in 'PREPARING' state.

        Parameters
        ----------
        database : list[dict]
            Map database.
        map_coords : str
            Current map's coordinates.

        Returns
        ----------
        char_coords : Tuple[int, int]
            `tuple` containing (x, y) coordinates of character.
        color : str
            Color of starting cell.

        """
        # Getting all possible starting cells on current map.
        for _, value in enumerate(database):
            for i_key, i_value in value.items():
                if map_coords == i_key:
                    cell_coordinates_list = i_value["cell"]

        # Getting character's coordinates.
        char_coords = cbt.Combat.get_char_position()

        # Calculating distances between char. coords and cells.
        distances = {}
        for coord in cell_coordinates_list:
            distance = ((coord[0] - char_coords[0]) ** 2 
                      + (coord[1] - char_coords[0]) ** 2)\
                      ** 0.5
            distances.update({coord: distance})

        # Setting the closest cell as current char. coordinates.
        for key, value in distances.items():
            if value == min(distances.values()):
                char_coords = key
                break

        # Getting the color of starting cell.
        color = self.__controller.preparing.get_start_cell_color(
            map_coords,
            database,
            char_coords
        )

        return char_coords, color

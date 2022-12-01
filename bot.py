"""Main bot logic."""

from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True)

import threading
import time
import os
import random

import cv2 as cv
import pyautogui

import bank
import combat as cbt
import data
import detection as dtc
import game_window as gw
import pop_up as pu

import state
from state.botstate_enum import BotState

import threading_tools as tt
import window_capture as wc


class Bot:
    """
    Main bot class.

    Logic flow is controlled by '__Bot_Thread_run()'.
    
    Methods
    ----------  
    Bot_Thread_start()
        Start bot thread.
    Bot_Thread_stop()
        Stop bot thread.

    """

    # Private class attributes.
    # Stores currently needed map data.
    __data_map = None
    # Stores loaded map data based on 'self.__script'.
    __data_map_hunting = None
    __data_map_banking = None
    # Stores monster image data.
    __data_monsters = None

    # Threading attributes.
    # 'Bot_Thread' threading attributes.
    __Bot_Thread_stopped = True
    __Bot_Thread_thread = None

    # 'BotState' attributes.
    #-----------------------
    # 'BotState.CONTROLLER'.
    # Stores if map that character is on was searched for monsters.
    # Helps '__controller' determine which 'BotState' to set.
    __map_searched = False
    # Stores current map's coordinates.
    __map_coords = None
    # Store maximum allowed pod percentage, bot banks when reached.
    # If character has at least 1 pod taken, the calculated % will be 
    # '14'.
    __pod_limit = 90
    # Counts total fights. Used to determine if it's time to check pods.
    __fight_counter = 0
    # Is character overloaded with pods or not.
    __character_overloaded = False

    # 'BotState.PREPARING'.
    # Info of cell the combat was started on.
    __cell_coords = None
    __cell_color = None
    __tactical_mode = False
    __cell_selection_failed = False

    # 'BotState.FIGHTING'.
    # Counts total completed fights. Just for statistics.
    __total_fights = 0
    # Stores if character failed to move during combat.
    __failed_to_move = False

    # 'BotState.BANKING'.
    # If 'Recall Potion' was used.
    __recall_potion_used = False

    # 'BotState.RECOVERY'.
    # Counts how many times emergency teleport was used.
    __emergency_teleports = 0

#----------------------------------------------------------------------#
#-----------------------------CONSTRUCTOR------------------------------#
#----------------------------------------------------------------------#

    def __init__(self,
                 script: str,
                 character_name: str,
                 official_version: bool = False,
                 debug_window: bool = True,
                 bot_state: str = BotState.INITIALIZING):
        """
        Constructor

        Parameters
        ----------
        script : str
            Bot script to load. Available: 'af_anticlock',
            'af_clockwise'.
        character_name : str
            Character's nickname.
        official_version : bool, optional
            Controls whether on official or private 'Dofus Retro' 
            servers. Official = `True`. Defaults to `False`.
        debug_window : bool, optional
            Whether to open visual debug window. Defaults to: `True`.
        bot_state : str, optional
            Current state of bot. Defaults to: `BotState.INITIALIZING`.

        """
        self.__official_version = official_version
        self.__state = bot_state

        state.Initializing.script = script
        state.Initializing.character_name = character_name
        state.Initializing.official_version = official_version
        state.Initializing.debug_window = debug_window

        gw.GameWindow.character_name = character_name
        gw.GameWindow.official_version = official_version

        cbt.Combat.character_name = character_name

        bank.Bank.official_version = official_version

#----------------------------------------------------------------------#
#--------------------------BOT STATE METHODS---------------------------#
#----------------------------------------------------------------------#

    def __controller(self):
        """Set bot state according to situation."""

        if self.__official_version:
            pu.PopUp.close_right_click_menu()
            if not state.Initializing.in_group():
                log.critical("Character is not in group!")
                log.critical("Exiting ... ")
                wc.WindowCapture.on_exit_capture()

        if self.__fight_counter % 6 == 0:
            # Incrementing by '1' instantly so bot doesn't check pods
            # everytime 'controller' is called.
            self.__fight_counter += 1
            # Getting pods percentage.
            pods_percentage = bank.Bank.get_pods_percentage()

            if pods_percentage >= self.__pod_limit:
                log.info("Overloaded! Going to bank ... ")
                self.__character_overloaded = True
            else:
                log.info("Not overloaded!")
                self.__character_overloaded = False

        if self.__character_overloaded:
            self.__data_map = self.__data_map_banking
            self.__map_coords = state.Moving.get_coordinates(self.__data_map)
            self.__state = BotState.BANKING

        elif not self.__character_overloaded:
            self.__data_map = self.__data_map_hunting
            self.__map_coords = state.Moving.get_coordinates(self.__data_map)
            map_type = state.Moving.get_map_type(
                    self.__data_map,
                    self.__map_coords
                )

            if map_type == "fightable":

                if self.__map_searched == False:
                    self.__state = BotState.HUNTING

                elif self.__map_searched == True:
                    self.__state = BotState.MOVING

            elif map_type == "traversable":
                self.__state = BotState.MOVING

            else:
                log.critical(f"Invalid map type '{map_type}' for map "
                             f"'{self.__map_coords}'!")
                log.critical(f"Exiting ... ")
                wc.WindowCapture.on_exit_capture()

    def __preparing(self):
        """'PREPARING' state logic."""
        # Resetting both values, so the 'output_image' in 
        # '__VisualDebugWindow_Thread_run()' is clean.
        self.__obj_rects = []
        self.__obj_coords = []
        # Stores whether to check for dummy cells. Always checks on
        # first iteration of loop.
        check_for_dummy_cells = True
        # Loop control variables.
        start_time = time.time()
        allowed_time = 45
        # Giving time for monsters to load before starting to check for 
        # empty cells. If ommited, may return false empty cell values
        # on first iteration of loop.
        time.sleep(0.5)

        while time.time() - start_time < allowed_time:

            if not self.__tactical_mode:
                if self.__preparing_enable_tactical_mode():
                    self.__tactical_mode = True

            if self.__tactical_mode:

                if check_for_dummy_cells:

                    check_for_dummy_cells = False
                    if self.__preparing_check_dummy_cells(self.__map_coords,
                                                          self.__data_map):
                        self.__preparing_select_dummy_cells()

                else:

                    if self.__preparing_select_starting_cell():
                        self.__state = BotState.FIGHTING
                        break
                    else:
                        continue

        else:
            log.critical(f"Failed to select starting cell in '{allowed_time}' "
                         "seconds!")
            log.critical("Exiting ... ")
            wc.WindowCapture.on_exit_capture()

    def __preparing_select_starting_cell(self):
        """Select starting cell and start combat."""
        failed_attempts = 0
        attempts_allowed = 2

        log.info(f"Trying to move character to starting cell ... ")

        while True:

            cells = self.__preparing_get_cells_from_database(self.__map_coords,
                                                             self.__data_map)
            e_cells = self.__preparing_get_empty_cells(cells)

            if len(e_cells) <= 0:
                self.__map_coords = state.Moving.get_coordinates(self.__data_map)
                continue

            if self.__preparing_move_char_to_cell(e_cells):

                self.__cell_color = self.__preparing_get_start_cell_color(
                                            self.__map_coords,
                                            self.__data_map,
                                            self.__cell_coords
                                        )

                if self.__preparing_start_combat():
                    log.info(f"Successfully selected starting cell!")
                    return "combat_start"

            else:

                if failed_attempts < attempts_allowed:
                    self.__map_coords = state.Moving.get_coordinates(self.__data_map)
                    failed_attempts += 1
                    continue

                else:
                    log.error("Cell selection failed!")
                    log.info("Trying to start combat ... ")
                    if self.__preparing_start_combat():
                        self.__cell_selection_failed = True                           
                        return "selection_fail"

    def __preparing_select_dummy_cells(self):
        """
        Select dummy cell to make starting cells visible.
        
        On certain maps character might spawn on a starting cell and
        block visibility of another starting cell. This method moves
        character out of the way so that all starting cells are visible.

        """
        failed_attempts = 0
        attempts_allowed = 1

        log.info("Trying to move character to dummy cell ... ")

        while True:

            cells = self.__preparing_get_dummy_cells(self.__map_coords,
                                                     self.__data_map)
            e_cells = self.__preparing_get_empty_cells(cells)

            if len(e_cells) <= 0:
                self.__map_coords = state.Moving.get_coordinates(self.__data_map)
                continue

            if self.__preparing_move_char_to_cell(e_cells):
                log.info("Successfully moved character to dummy cell!")
                return True

            else:

                if failed_attempts < attempts_allowed:
                    self.__map_coords = state.Moving.get_coordinates(self.__data_map)
                    failed_attempts += 1
                    continue
                else:
                    log.error("Failed to move character to dummy cell!")
                    return False

    def __preparing_check_dummy_cells(self, map_coords, database):
        """Check if map has dummy cells."""

        log.info("Checking for dummy cells ... ")

        for _, value in enumerate(database):
            for i_key, i_value in value.items():
                if map_coords == i_key:
                    if "d_cell" in i_value.keys():
                        log.info("Dummy cells available!")
                        return True
                    else:
                        log.info("No dummy cells available on this map!")
                        return False

    def __preparing_get_dummy_cells(self, map_coords, database):
        """Get current map's dummy cells."""
        for _, value in enumerate(database):
            for i_key, i_value in value.items():
                if map_coords == i_key:
                    cell_coordinates_list = i_value["d_cell"]
                    return cell_coordinates_list

    def __preparing_enable_tactical_mode(self):
        """Enable tactical mode."""
        # Wait time after clicking on 'Tactical Mode' icon. Giving time
        # for green check mark to appear.
        wait_time_click = 0.25
        # Colors.
        c_green = (0, 153, 0)
        c_gray = (216, 202, 150)
        # Loop control variables.
        start_time = time.time()
        wait_time = 7

        while time.time() - start_time < wait_time:

            group = pyautogui.pixelMatchesColor(818, 526, c_gray)

            if group:
                tactical_mode = pyautogui.pixelMatchesColor(790, 526, c_green)
                if not tactical_mode:
                    log.info("Enabling 'Tactical Mode' ... ")
                    pyautogui.moveTo(790, 526, duration=0.15)
                    pyautogui.click()
                    time.sleep(wait_time_click)
                else:
                    log.info("'Tactical Mode' enabled!")
                    return True

            else:
                tactical_mode = pyautogui.pixelMatchesColor(817, 524, c_green)
                if not tactical_mode:
                    log.info("Enabling 'Tactical Mode' ... ")
                    pyautogui.moveTo(817, 524, duration=0.15)
                    pyautogui.click()
                    time.sleep(wait_time_click)
                else:
                    log.info("'Tactical Mode' enabled!")
                    return True

        else:
            log.error(f"Failed to enable in {wait_time} seconds!")
            return False

    def __preparing_get_cells_from_database(self, map_coords, database):
        """
        Get map's starting cell coordinates from database.
        
        Parameters
        ----------
        map_coords : str
            Map's coordinates as `str`.
        database : list[dict]
            `list` of `dict` from script's 'Hunting.data'.
        
        Returns
        ----------
        cell_coordinates_list : list[Tuple[int, int]]
            `list` of `tuple` containing [(x, y)] coordinates of cells.
        
        """
        for _, value in enumerate(database):
            for i_key, i_value in value.items():
                if map_coords == i_key:
                    cell_coordinates_list = i_value["cell"]
                    return cell_coordinates_list

    def __preparing_get_empty_cells(self, cell_coordinates_list):
        """
        Get empty cell coordinates from cell coordinates list.

        Logic
        ----------
        - Check for red and blue pixels on every (x, y) coordinate in
        `cell_coordinates_list`.
        - Append every coordinate where pixels were found to 
        `empty_cells_list`

        Parameters
        ----------
        cell_coordinates_list : list[Tuple[int, int]]
            `list` of `tuple` containing [(x, y)] coordinates of cells.
        
        Returns
        ----------
        empty_cells_list : list[Tuple[int, int]]
            `list` of `tuple` containing [(x, y)] coordinates of empty
            cells.
        
        """
        empty_cells_list = []
        colors = [(255, 0, 0), (154, 0, 0), (0, 0, 255), (0, 0, 154)]

        for coords in cell_coordinates_list:
            for color in colors:
                px = pyautogui.pixelMatchesColor(coords[0], coords[1], color)
                if px:
                    empty_cells_list.append(coords)

        return empty_cells_list

    def __preparing_get_start_cell_color(self,
                                         map_coords,
                                         database,
                                         start_cell_coords):
        """
        Get combat start cell color.

        Parameters
        ----------
        map_coords : str
            Map's coordinates as `str`.
        database : list[dict]
            `list` of `dict` from script's 'Hunting.data'.
        start_cell_coords : Tuple[int, int]
            Starting cell's (x, y) coordinates.

        Returns
        ----------
        str
            Color of starting cell.

        """
        cells_list = self.__preparing_get_cells_from_database(
                map_coords,
                database,
            )

        index = cells_list.index(start_cell_coords)

        if index <= 1:
            return "red"
        elif index >= 2:
            return "blue"

    def __preparing_move_char_to_cell(self, cell_coordinates_list):
        """
        Move character to cell.

        Also saves the starting cell coordinates for use in "FIGHTING"
        state.
        
        Parameters
        ----------
        cell_coordinates_list : list[Tuple[int, int]]
            `list` of `tuple` containing [(x, y)] coordinates of cells.

        Returns
        ----------
        True : bool
            If character was moved successfully.
        False : bool
            If character wasn't moved.
        
        """
        # Time to wait after moving character to cell. If omitted,
        # '__preparing_check_if_char_moved()' starts checking before 
        # character has time to move and gives false results.
        wait_after_move_char = 0.5

        for cell in cell_coordinates_list:
            log.info(f"Moving character to cell: {cell} ... ")
            pyautogui.moveTo(cell[0], cell[1])
            pyautogui.click()
            time.sleep(wait_after_move_char)
            if self.__preparing_check_if_char_moved(cell):
                self.__cell_coords = cell
                return True
        return False

    def __preparing_check_if_char_moved(self, cell_coordinates):
        """
        Check if character moved to cell.

        Checks for red and blue colored pixels on `cell_coordinates`. If
        none were found it means character is standing there.
        
        Parameters
        ----------
        cell_coordinates : Tuple[int, int]

        Returns
        ----------
        True : bool
            If character was moved successfully.
        False : bool
            If character wasn't moved.
        
        """
        pixels = []
        colors = [
            (255, 0, 0), (154, 0, 0), (0, 0, 255), (0, 0, 154), (85, 81, 56)
        ]
        
        for color in colors:
            px = pyautogui.pixelMatchesColor(cell_coordinates[0],
                                             cell_coordinates[1],
                                             color)
            pixels.append(px)

        if not any(pixels):
            log.info("Character moved successfully!")
            return True
        else:
            log.info("Failed to move character!")
            return False

    def __preparing_start_combat(self):
        """Click ready to start combat."""
        # Time to wait after clicking ready. How long to keep chacking 
        # if combat was started successfully.
        wait_combat_start = 5
        # 'Ready' button state.
        ready_button_clicked = False
        # Controls if clicking 'Ready' first time. Will click twice
        # after failing the first time.
        first_try = True
        # Loop control variables.
        timeout = 15
        start_time = time.time()

        # Getting (x, y) coords of 'Ready' button.
        while time.time() - start_time < timeout:

            screenshot = wc.WindowCapture.gamewindow_capture()
            ready_button_icon = dtc.Detection.get_click_coords(
                    dtc.Detection.find(
                            screenshot,
                            data.images.Status.preparing_sv_2,
                            threshold=0.8
                        )
                    )

            if len(ready_button_icon) > 0:
                x, y = ready_button_icon[0][0], ready_button_icon[0][1]
                break

        else:
            log.critical(f"Failed to locate 'Ready' button!")
            log.critical("Exiting ... ")
            wc.WindowCapture.on_exit_capture()

        # Clicking 'Ready' to start combat.
        while True:

            # If 'Ready' button wasn't clicked.
            if not ready_button_clicked:

                log.info("Clicking 'READY' ... ")
                pyautogui.moveTo(x, y, duration=0.15)
                if first_try:
                    pyautogui.click()
                else:
                    pyautogui.click(clicks=2, interval=0.1)
                # Moving the mouse off the 'Ready' button in case it 
                # needs to be detected again.
                pyautogui.move(0, 80)
                click_time = time.time()
                ready_button_clicked = True 

            # Checking if combat started after 'Ready' was clicked.
            if ready_button_clicked:

                screenshot = wc.WindowCapture.gamewindow_capture()
                cc_icon = dtc.Detection.find(
                        screenshot,
                        data.images.Status.fighting_sv_1,
                        threshold=0.8
                    )
                ap_icon = dtc.Detection.find(
                        screenshot, 
                        data.images.Status.fighting_sv_2,
                        threshold=0.8
                    )
                mp_icon = dtc.Detection.find(
                        screenshot,
                        data.images.Status.fighting_sv_3,
                        threshold=0.8
                    )
                
                if time.time() - click_time > wait_combat_start:
                    log.error("Failed to start combat!")
                    log.error("Retrying ... ")
                    ready_button_clicked = False
                    first_try = False
                    continue

                if len(cc_icon) > 0 and len(ap_icon) > 0 and len(mp_icon) > 0:
                    log.info("Successfully started combat!")
                    return True

    def __fighting(self):
        """'FIGHTING' state logic."""
        first_turn = True
        tbar_shrunk = False
        character_moved = False
        models_hidden = False
        start_time = time.time()
        timeout = 300

        while time.time() - start_time < timeout:

            if cbt.Combat.turn_detect_start():

                if not tbar_shrunk:
                    if cbt.Combat.shrink_turn_bar():
                        tbar_shrunk = True

                if not models_hidden:
                    if cbt.Combat.hide_models():
                        models_hidden = True

                if not character_moved:
                    if self.__fighting_move_character():
                        character_moved = True

                if character_moved and first_turn:
                    if self.__fighting_cast_spells(first_turn=True):
                        if cbt.Combat.turn_pass():
                            log.info("Waiting for turn ... ")
                            first_turn = False
                            continue

                elif character_moved and not first_turn:
                    if self.__fighting_cast_spells(first_turn=False):
                        if cbt.Combat.turn_pass():
                            log.info("Waiting for turn ... ")
                            continue

            elif self.__fighting_detect_end_of_fight():
                self.__fight_counter += 1
                self.__total_fights += 1
                self.__state = BotState.CONTROLLER
                log.info(f"Total fights: {self.__total_fights} ... ")
                break

        else:
            log.critical(f"Failed to complete fight actions in {timeout} "
                         "seconds!")
            log.critical("Timed out!")
            log.critical("Exiting ... ")
            wc.WindowCapture.on_exit_capture()

    def __fighting_move_character(self):
        """Move character."""
        attempts = 0
        attempts_allowed = 3

        while attempts < attempts_allowed:

            if self.__cell_selection_failed:
                log.debug("Getting cell coords and color in 'fighting' ... ")
                # Giving time for 'Illustration to signal your turn' 
                # to disappear.
                time.sleep(3)
                self.__cell_coords, self.__cell_color = \
                    self.__fighting_get_cell_coords_and_color(
                            self.__map_coords
                        )
                self.__cell_selection_failed = False

            move_coords = cbt.Combat.get_movement_coordinates(
                    self.__map_coords,
                    self.__cell_color,
                    self.__cell_coords,
                )

            if cbt.Combat.get_if_char_on_correct_cell(move_coords):
                log.info("Character is standing on correct cell!")
                # Moving mouse cursor off character so that spell bar
                # is visible and ready for detection.
                pyautogui.moveTo(x=609, y=752)
                return True

            else:
                log.info("Moving character ... ")
                cbt.Combat.move_character(move_coords)

                start_time = time.time()
                wait_time = 3

                while time.time() - start_time < wait_time:
                    if cbt.Combat.get_if_char_on_correct_cell(move_coords):
                        pyautogui.moveTo(x=609, y=752)
                        return True
                else:
                    attempts += 1

        else:
            self.__failed_to_move = True
            log.error(f"Failed to move character in {attempts} attempts!")
            log.debug(f"'self.__failed_to_move' = {self.__failed_to_move}")
            return True

    def __fighting_get_cell_coords_and_color(self, map_coords):
        """
        Get starting cell color and coords.

        Only used when usual logic of starting cell selection fails
        in 'PREPARING' state.

        Parameters
        ----------
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
        for _, value in enumerate(self.__data_map_hunting):
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
        color = self.__preparing_get_start_cell_color(
                map_coords,
                self.__data_map_hunting,
                char_coords
            )

        return char_coords, color

    def __fighting_cast_spells(self, first_turn):
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
        timeout = 20

        while time.time() - start_time < timeout:

            available_spells = cbt.Combat.get_available_spells()

            if len(available_spells) <= 0:
                log.info("No spells available!")
                self.__failed_to_move = False
                return True

            if cast_times >= 5:
                log.debug(f"Setting first turn to 'False' due to too many "
                          "failed attempts to cast spells ... ")
                first_turn = False
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
                                self.__map_coords,
                                self.__cell_color,
                                self.__cell_coords
                            )

                elif not first_turn and get_char_pos:
                    cast_coords = cbt.Combat.get_char_position()
                    if cast_coords is None:
                        log.debug(f"cast_coords={cast_coords} ... ")
                        log.debug("Continuing ... ")
                        continue
                    else:
                        get_char_pos = False

                cbt.Combat.cast_spell(spell, spell_coords, cast_coords)
                cast_times += 1
                break

        else:
            log.critical(f"Failed to cast spells in {timeout} seconds!")
            log.critical("Exiting ... ")
            wc.WindowCapture.on_exit_capture()

    def __fighting_detect_results_window(self):
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

    def __fighting_detect_end_of_fight(self):
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
            close_button = self.__fighting_detect_results_window()

            if len(close_button) <= 0:
                return False

            elif len(close_button) > 0:

                log.info("Combat has ended!")
                start_time = time.time()
                timeout_time = 60

                while time.time() - start_time < timeout_time:

                    # Closing 'Fight Results' window.
                    close_button = self.__fighting_detect_results_window()
                    
                    if len(close_button) <= 0:
                        log.info("Successfully closed 'Fight Results' "
                                 "window!")
                        return True
                    else:
                        log.info("Closing 'Fight Results' window ... ")
                        pyautogui.moveTo(x=close_button[0][0],
                                         y=close_button[0][1],
                                         duration=0.15)
                        pyautogui.click()
                        # Moving mouse off the 'Close' button in case it 
                        # needs to be detected again.
                        pyautogui.move(100, 0)

                        # Checking for offers/interfaces and closing them.
                        pu.PopUp.deal()

                else:
                    log.critical("Couldn't close 'Fight Results' window in "
                                 f"{timeout_time} second(s)!")
                    log.critical("Timed out!")
                    log.critical("Exiting ... ")
                    wc.WindowCapture.on_exit_capture()

    def __banking(self):
        """
        Banking logic.

        Logic
        ----------
        - If 'Recall Potion' wasn't used:
            - Use it.
        - Elif character on "4,-16" map:
            - Launch 'Astrub Bank' banking logic.
        - Else:
            - Change 'BotState' to 'MOVING'.

        """
        while True:

            if not self.__recall_potion_used:
                if bank.Bank.recall_potion() == "available":
                    self.__banking_use_recall_potion()
                    self.__recall_potion_used = True
                else:
                    self.__recall_potion_used = True

            elif self.__map_coords == "4,-16":
                if self.__banking_astrub_bank():
                    self.__recall_potion_used = False
                    self.__state = BotState.CONTROLLER
                    return

            else:
                self.__state = BotState.MOVING
                return

    def __banking_use_recall_potion(self):
        """
        Use 'Recall Potion'.
        
        Make sure that an appropriate Zaap is saved on character. 
        For example, when using 'Astrub Forest' script, Astrub's Zaap 
        should be saved.

        """
        use_time = time.time()
        timeout = 15

        while time.time() - use_time < timeout:

            pu.PopUp.deal()
            bank.Bank.use_recall_potion()
            self.__map_coords = state.Moving.get_coordinates(self.__data_map)

            if self.__map_coords == "4,-19":
                log.info("Successfully used 'Recall Potion'!")
                return True

        else:
            log.error(f"Failed to use 'Recall Potion' in {timeout} seconds!")
            return False

    def __banking_astrub_bank(self):
        """
        'Astrub Bank' banking logic.
        
        - Close any pop-ups & interfaces.
        - Detect if inside or outside Astrub bank.
            - If not inside:
                - Move character inside.
            - Elif inside and items have been deposited:
                - Move character outside.
            - Elif inside ant items have not been deposited:
                - Open bank, deposit, close bank and return `True`.

        Program will exit if: 
        - `attempts_total` < `attempts_allowed`.
        - `timeout` seconds reached.
        
        """
        attempts_total = 0
        attempts_allowed = 5
        items_deposited = False

        while attempts_total < attempts_allowed:

            pu.PopUp.deal()
            character_inside_bank = bank.Bank.inside_or_outside()

            if not character_inside_bank:
                if bank.Bank.enter_bank():
                    continue
                else:
                    attempts_total += 1

            elif character_inside_bank and items_deposited:
                if bank.Bank.exit_bank():
                    self.__fight_counter = 0
                    return True
                else:
                    attempts_total += 1
                    continue
                
            elif character_inside_bank and not items_deposited:

                start_time = time.time()
                timeout = 60

                while time.time() - start_time < timeout:
                    pu.PopUp.deal()
                    if bank.Bank.open_bank_vault():
                        if bank.Bank.deposit_items():
                            if bank.Bank.close_bank_vault():
                                items_deposited = True
                                break

                else:
                    log.critical("Failed to complete actions inside "
                                 f"bank in {timeout} seconds!")
                    log.critical("Timed out!")
                    log.critical("Exiting ... ")
                    wc.WindowCapture.on_exit_capture()

        else:
            log.critical("Failed to enter/exit bank in "
                         f"{attempts_allowed} attempts!")
            log.critical("Exiting ... ")
            wc.WindowCapture.on_exit_capture()

#----------------------------------------------------------------------#
#------------------------MAIN THREAD OF CONTROL------------------------#
#----------------------------------------------------------------------#

    def __Bot_Thread_run(self):
        """Execute this code while bot thread is alive."""
        try:

            while not self.__Bot_Thread_stopped:

                # Makes bot ready to go. Always starts in this state.
                if self.__state == BotState.INITIALIZING:
                    self.__state = state.Initializing.initializing()
                    self.__data_map_hunting = state.Initializing.data_hunting
                    self.__data_map_banking = state.Initializing.data_banking
                    self.__data_monsters = state.Initializing.data_monsters

                # Determines what state to switch to when out of combat.
                elif self.__state == BotState.CONTROLLER:
                    self.__controller()

                # Handles detection and attacking of monsters.
                elif self.__state == BotState.HUNTING:
                    state.Hunting.data_monsters = self.__data_monsters
                    state.Hunting.map_coords = self.__map_coords       
                    self.__state, self.__map_searched = state.Hunting.hunting()

                # Handles combat preparation.
                elif self.__state == BotState.PREPARING:
                    self.__preparing()

                # Handles combat.
                elif self.__state == BotState.FIGHTING:
                    self.__fighting()
                            
                # Handles map changing.
                elif self.__state == BotState.MOVING:
                    state.Moving.map_coords = self.__map_coords
                    state.Moving.data_map = self.__data_map
                    self.__state, self.__map_searched = state.Moving.moving()

                # Handles banking.
                elif self.__state == BotState.BANKING:
                    self.__banking()

        except:

            log.exception("An exception occured!")
            log.critical("Exiting ... ")
            wc.WindowCapture.on_exit_capture()

#----------------------------------------------------------------------#
#--------------------------THREADING METHODS---------------------------#
#----------------------------------------------------------------------#

    def Bot_Thread_start(self):
        """Start bot thread."""
        self.__Bot_Thread_stopped = False
        self.__Bot_Thread_thread = threading.Thread(
                target=self.__Bot_Thread_run
            )
        self.__Bot_Thread_thread.start()
        tt.ThreadingTools.wait_thread_start(self.__Bot_Thread_thread)

    def Bot_Thread_stop(self):
        """Stop bot thread."""
        self.__Bot_Thread_stopped = True
        self.__VisualDebugWindow_Thread_stop()
        tt.ThreadingTools.wait_thread_stop(self.__Bot_Thread_thread)

#----------------------------------------------------------------------#

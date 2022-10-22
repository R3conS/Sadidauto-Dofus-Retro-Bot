"""Main bot logic."""

import threading
import time
import os
import random

import cv2 as cv
import pyautogui

from bank import Bank
from combat import Combat
from data import ImageData, MapData, CombatData
from detection import Detection
from game_window import GameWindow
from pop_up import PopUp
from threading_tools import ThreadingTools
from window_capture import WindowCapture


class BotState:
    """Bot states enum."""

    INITIALIZING = "INITIALIZING"
    CONTROLLER = "CONTROLLER"
    SEARCHING = "SEARCHING"
    ATTACKING = "ATTACKING"
    PREPARATION = "PREPARATION"
    IN_COMBAT = "IN_COMBAT"
    CHANGING_MAP = "CHANGING_MAP"
    BANKING = "BANKING"


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
    # Pyautogui mouse movement duration. Default is '0.1' as per docs.
    __move_duration = 0.15
    # Stores currently needed map data.
    __data_map = None
    # Stores loaded map data based on 'self.__script'.
    __data_map_killing = None
    __data_map_banking = None
    # Stores monster image data and path to the folder with the images.
    __data_objects_list = None
    __data_objects_path = None

    # Threading attributes.
    # 'Bot_Thread' threading attributes.
    __Bot_Thread_stopped = True
    __Bot_Thread_thread = None
    # 'Window_VisualDebugOutput_Thread' threading attributes.
    __VisualDebugWindow_Thread_stopped = True
    __VisualDebugWindow_Thread_thread = None

    # Objects.
    __threading_tools = ThreadingTools()
    __window_capture = WindowCapture()
    __detection = Detection()
    __bank = Bank()
    __popup = PopUp()

    # 'BotState' attributes.
    #-----------------------
    # 'BotState.CONTROLLER'.
    # Stores if map that character is on was searched for monsters.
    # Helps '__controller' determine which 'BotState' to set.
    __map_searched = False
    # Stores current map's coordinates.
    __map_coordinates = None
    # Store maximum allowed pod percentage, bot banks when reached.
    # If character has at least 1 pod taken, the calculated % will be 
    # '14'.
    __pod_limit = 85
    # Counts total fights. Used to determine if it's time to check pods.
    __fight_counter = 0
    # Is character overloaded with pods or not.
    __character_overloaded = False

    # 'BotState.SEARCHING'.
    __obj_rects = []
    __obj_coords = []

    # 'BotState.ATTACKING'.
    # Failed attack attempts allowed before searching for monsters.
    __attack_attempts_allowed = 3

    # 'BotState.PREPARATION'.
    # Info of cell the combat was started on.
    __preparation_combat_start_cell_coords = None
    __preparation_combat_start_cell_color = None

    # 'BotState.IN_COMBAT'.
    # Counts total completed fights. Just for statistics.
    __total_fights = 0

#----------------------------------------------------------------------#
#-----------------------------CONSTRUCTOR------------------------------#
#----------------------------------------------------------------------#

    def __init__(self,
                 character_name: str,
                 official_version: bool,
                 script: str,
                 debug_window: bool = False,
                 detection_threshold: float = 0.6,
                 bot_state: str = BotState.INITIALIZING):
        """
        Constructor

        Parameters
        ----------
        character_name : str
            Character's nickname.
        official_version : bool
            Controls whether on official or private 'Dofus Retro' 
            servers. Official = `True`.
        script : str
            Bot script to load. Available: 'astrub_forest',
            'astrub_forest_reversed'.
        debug_window : bool, optional
            Whether to open visual debug window. Defaults to: `False`.
        detection_threshold : bool, optional
            Controls threshold value for `detect_objects()` in
            `BotState.SEARCHING`. Defaults to 0.6.
        bot_state : str, optional
            Current state of bot. Defaults to: `BotState.INITIALIZING`.

        """
        self.__script = script
        self.__debug_window = debug_window
        self.__detection_threshold = detection_threshold
        self.__state = bot_state
        self.__game_window = GameWindow(character_name, official_version)
        self.__combat = Combat(character_name)
        
#----------------------------------------------------------------------#
#-------------------------------METHODS--------------------------------#
#----------------------------------------------------------------------#

    def __check_if_map_in_database(self, map, database):
        """
        Check if map is in database.

        Parameters
        ----------
        map : str
            Map to check.
        database : list[dict]
            Database to check in.

        Returns
        ----------
        True : bool
            If `map` is in `database`.
        False : bool
            If `map` is NOT in `database`.

        """
        maps = []
        for _, value in enumerate(database):
            for key in value.keys():
                maps.append(key)

        if map not in maps:
            return False

        return True

    def __get_current_map_coordinates(self, map_database):
        """
        Get current map's coordinates.

        Parameters
        ----------
        map_database : list[dict]
            Map's database.
        
        Returns
        ----------
        map_coords : str
            Map coordinates as a `str`.
        False : bool
            If map wasn't detected.
        NoReturn
            If detected map doesn't exist in database.

        """
        # Giving time for black tooltip that shows map coordinates to
        # appear. Otherwise on a slower machine the program might take a
        # screenshot too fast resulting in an image with no coordinates
        # to detect.
        wait_before_detecting = 0.25
        # Loop control variables.
        start_time = time.time()
        wait_time_before_exit = 60

        while time.time() - start_time < wait_time_before_exit:

            # Checking for offers/interfaces and closing them.
            self.__popup.deal()

            # Get a screenshot of coordinates on minimap. Moving mouse
            # over the red area on the minimap for the black map tooltip
            # to appear.
            pyautogui.moveTo(517, 680)
            time.sleep(wait_before_detecting)
            screenshot = self.__window_capture.custom_area_capture(
                    capture_region=self.__window_capture.MAP_DETECTION_REGION,
                    conversion_code=cv.COLOR_RGB2GRAY,
                    interpolation_flag=cv.INTER_LINEAR,
                    scale_width=215,
                    scale_height=200
                )
            # Moving mouse off the red area on the minimap in case a new 
            # screenshot is required for another detection.
            pyautogui.move(20, 0)

            # Get map coordinates as a string.
            r_and_t, _, _ = self.__detection.detect_text_from_image(screenshot)
            try:
                map_coords = r_and_t[0][1]
                map_coords = map_coords.replace(".", ",")
            except IndexError:
                continue

            if self.__check_if_map_in_database(map_coords, map_database):
                return map_coords
            else:
                print(f"[ERROR] Map ({map_coords}) doesn't exist in database!")
                print("[ERROR] Exiting ... ")
                os._exit(1)

        else:
            print("[ERROR] Fatal error in "
                  "'__get_current_map_coordinates()'!")
            print("[ERROR] Exceeded detection time limit of "
                  f"{wait_time_before_exit} second(s)!")
            print("[ERROR] Exiting ... ")
            os._exit(1)

    def __get_map_type(self, map_coordinates):
        """
        Get current map's type.
        
        Parameters
        ----------
        map_coordinates : str
            Current map's coordinates.

        Returns
        ----------
        map_type : str
            Current map's type.
        
        """
        for _, value in enumerate(self.__data_map):
            for i_key, i_value in value.items():
                if map_coordinates == i_key:
                    map_type = i_value["map_type"]
                    return map_type

#----------------------------------------------------------------------#
#--------------------------BOT STATE METHODS---------------------------#
#----------------------------------------------------------------------#

    def __initializing(self):
        """Initializing state logic."""
        # Making sure 'Dofus.exe' is launched and char is logged in.
        if self.__game_window.check_if_exists():
            self.__game_window.resize_and_move()
        else:
            os._exit(1)

        # Starts 'Window_VisualDebugOutput_Thread' if needed.
        if self.__debug_window:
            self.__VisualDebugWindow_Thread_start()

        # Loading bot script data.
        if self.__initializing_load_bot_script_data(self.__script):
            print(f"[INFO] Successfully loaded '{self.__script}' script!")

        # Passing control to 'CONTROLLER' state.
        print(f"[INFO] Changing 'BotState' to: '{BotState.CONTROLLER}' ... ")
        self.__state = BotState.CONTROLLER

    def __initializing_load_bot_script_data(self, script):
        """
        Load data based on `script`.

        Parameters
        ----------
        script : str
            Name of bot `script`.
        
        Returns
        ----------
        True : bool
            If `script` was loaded successfully.
        NoReturn
            Exits program if `script` is not `str` or if `script` is not
            among valid/available scripts.
        
        """
        if not isinstance(script, str):
            print("[ERROR] Parameter 'script' must be a string ... ")
            print("[ERROR] Exiting ... ")
            os._exit(1)

        script = script.lower()

        if script == "astrub_forest":
            self.__data_map_killing = MapData.AstrubForest.killing
            self.__data_map_banking = MapData.AstrubForest.banking
            self.__data_objects_path = ImageData.AstrubForest.monster_img_path
            self.__data_objects_list = ImageData.AstrubForest.monster_img_list
            self.__combat.data_spell_cast = CombatData.Spell.AstrubForest.af
            self.__combat.data_movement = CombatData.Movement.AstrubForest.af
            self.__bank.img_path = ImageData.AstrubForest.banker_images_path
            self.__bank.img_list = ImageData.AstrubForest.banker_images_list
            # self.__data_objects_path = ImageData.test_monster_images_path
            # self.__data_objects_list = ImageData.test_monster_images_list
            self.__script = "Astrub Forest"
            return True

        elif script == "astrub_forest_reversed":
            self.__data_map_killing = MapData.AstrubForest.killing_reversed
            self.__data_map_banking = MapData.AstrubForest.banking
            self.__data_objects_path = ImageData.AstrubForest.monster_img_path
            self.__data_objects_list = ImageData.AstrubForest.monster_img_list
            self.__combat.data_spell_cast = CombatData.Spell.AstrubForest.af
            self.__combat.data_movement = CombatData.Movement.AstrubForest.af
            self.__bank.img_path = ImageData.AstrubForest.banker_images_path
            self.__bank.img_list = ImageData.AstrubForest.banker_images_list
            self.__script = "Astrub Forest - Reversed"
            return True

        else:
            print(f"[ERROR] Couldn't find script '{script}' in database ... ")
            print("[ERROR] Exiting ... ")
            os._exit(1)

    def __controller(self):
        """Set bot state according to situation."""
        if self.__fight_counter % 6 == 0:
            # Incrementing by '1' instantly so bot doesn't check pods
            # everytime 'controller' is called.
            self.__fight_counter += 1

            pods_percentage = self.__bank.get_pods_percentage()

            if pods_percentage >= self.__pod_limit:
                print("[INFO] Overloaded! Going to bank ... ")
                self.__character_overloaded = True
            else:
                print("[INFO] Not overloaded! Hunting ... ")
                self.__character_overloaded = False

        if self.__character_overloaded:
            self.__data_map = self.__data_map_banking
            self.__map_coordinates = self.__get_current_map_coordinates(
                    self.__data_map
                )
            self.__state = BotState.BANKING

        elif not self.__character_overloaded:
            self.__data_map = self.__data_map_killing
            self.__map_coordinates = self.__get_current_map_coordinates(
                    self.__data_map
                )
            map_type = self.__get_map_type(self.__map_coordinates)

            if map_type == "fightable":

                if self.__map_searched == False:
                    self.__state = BotState.SEARCHING

                elif self.__map_searched == True:
                    self.__state = BotState.CHANGING_MAP

            elif map_type == "traversable":
                self.__state = BotState.CHANGING_MAP

            else:
                print(f"[ERROR] Invalid map type '{map_type}' for map "
                        f"'{self.__map_coordinates}'!")
                print(f"[ERROR] Exiting ... ")
                os._exit(1)

    def __searching(self):
        """Searching state logic."""
        print(f"[INFO] Searching for monsters ... ")

        screenshot = self.__window_capture.gamewindow_capture()
        self.__obj_rects, self.__obj_coords = self.__detection.detect_objects(
                self.__data_objects_list,
                self.__data_objects_path,
                screenshot,
                threshold=self.__detection_threshold
            )

        # If monsters were detected.
        if len(self.__obj_coords) > 0:
            print(f"[INFO] Monsters found at: {self.__obj_coords}!")
            # print("[INFO] Changing 'BotState' to: "
            #       f"'{BotState.ATTACKING}' ... ")
            self.__state = BotState.ATTACKING
            self.__map_searched = False
                
        # If monsters were NOT detected.
        elif len(self.__obj_coords) <= 0:
            print("[INFO] Couldn't find any monsters!")
            # print("[INFO] Changing 'BotState' to: "
            #       f"'{BotState.CONTROLLER}' ... ")
            self.__state = BotState.CONTROLLER
            self.__map_searched = True

    def __attacking(self):
        """Attacking state logic."""
        if self.__attacking_attack_monster():
            self.__state = BotState.PREPARATION
        else:
            self.__state = BotState.CONTROLLER

    def __attacking_attack_monster(self):
        """
        Attack monster.
        
        Logic
        ----------
        - Get detected monster coordinates.
        - Attack monster.
            - If monster attacked successfully - return `True`.
            - If failed to attack monster - return `False`.

        Returns
        ----------
        True : bool
            If attack was successful.
        False : bool
            If attack was unsuccessful.

        """
        # Time to wait after clicking on a monster. How long script will 
        # keep chacking if the monster was successfully attacked.
        wait_after_attacking = 5
        # Flow control variables.
        attack_attempts_allowed = 0
        attack_attempts_total = 0

        # Allowing character to fail an attack no more than 
        # 'self.attack_attempts_allowed' times.
        if len(self.__obj_coords) > self.__attack_attempts_allowed:
            attack_attempts_allowed = self.__attack_attempts_allowed
        else:
            attack_attempts_allowed = len(self.__obj_coords)

        # Looping through detected monster coordinates.
        for coords in self.__obj_coords:

            # Checking for offers/interfaces and closing them.
            self.__popup.deal()

            x_coord, y_coord = coords

            # Separating moving mouse and clicking into two actions,
            # because otherwise it sometimes right clicks too early,
            # causing the character to fail an attack.
            print(f"[INFO] Attacking monster at: {coords} ... ")
            pyautogui.moveTo(x_coord, y_coord, duration=self.__move_duration)
            pyautogui.click(button="right")

            attack_time = time.time()
            while True:

                screenshot = self.__window_capture.gamewindow_capture()
                cc_icon = self.__detection.find(
                        screenshot,
                        ImageData.s_i + ImageData.preparation_sv_1
                    )
                ready_button = self.__detection.find(
                        screenshot,
                        ImageData.s_i + ImageData.preparation_sv_2
                    )
                
                if time.time() - attack_time > wait_after_attacking:
                    print(f"[INFO] Failed to attack monster at: {coords}!")
                    print("[INFO] Trying the next coordinates ... ")
                    attack_attempts_total += 1
                    break
                elif len(cc_icon) > 0 and len(ready_button) > 0:
                    print("[INFO] Successfully attacked monster at: "
                          f"{coords}!")
                    return True

            if (attack_attempts_allowed == attack_attempts_total):
                print("[INFO] Failed to start combat "
                      f"'{attack_attempts_total}' time(s)!")
                return False

    def __preparation(self):
        """Preparation state logic."""
        # Resetting both values, so the 'output_image' in 
        # '__VisualDebugWindow_Thread_run()' is clean.
        self.__obj_rects = []
        self.__obj_coords = []
        # 'Tactical Mode' status.
        tactical_mode = False
        # Loop control variables.
        start_time = time.time()
        allowed_time = 20

        while time.time() - start_time < allowed_time:

            if not tactical_mode:
                if self.__preparation_enable_tactical_mode():
                    tactical_mode = True

            if tactical_mode:
                cells = self.__preparation_get_cells_from_database(
                        self.__map_coordinates,
                        self.__data_map
                    )
                e_cells = self.__preparation_get_empty_cells(cells)
                if self.__preparation_move_char_to_cell(e_cells):
                    self.__preparation_combat_start_cell_color = \
                            self.__preparation_get_start_cell_color(
                                    self.__map_coordinates,
                                    self.__data_map,
                                    self.__preparation_combat_start_cell_coords
                                )
                    if self.__preparation_start_combat():
                        self.__state = BotState.IN_COMBAT
                        break

        else:
            print(f"[ERROR] Failed to select starting cell in '{allowed_time}'"
                  " seconds!")
            print("[ERROR] Exiting ... ")
            os._exit(1)

    def __preparation_enable_tactical_mode(self):
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
                    print("[INFO] Enabling 'Tactical Mode' ... ")
                    pyautogui.moveTo(790, 526, duration=self.__move_duration)
                    pyautogui.click()
                    time.sleep(wait_time_click)
                else:
                    print("[INFO] 'Tactical Mode' enabled!")
                    return True

            else:
                tactical_mode = pyautogui.pixelMatchesColor(817, 524, c_green)
                if not tactical_mode:
                    print("[INFO] Enabling 'Tactical Mode' ... ")
                    pyautogui.moveTo(817, 524, duration=self.__move_duration)
                    pyautogui.click()
                    time.sleep(wait_time_click)
                else:
                    print("[INFO] 'Tactical Mode' enabled!")
                    return True

        else:
            print(f"[INFO] Failed to enable in {wait_time} seconds!")
            return False

    def __preparation_get_cells_from_database(self, map_coords, database):
        """
        Get map's starting cell coordinates from database.
        
        Parameters
        ----------
        map_coords : str
            Map's coordinates as `str`.
        database : list[dict]
            `list` of `dict` from `MapData`.
        
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

    def __preparation_get_empty_cells(self, cell_coordinates_list):
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

        for cell_coordinates in cell_coordinates_list:

            red_pixel = pyautogui.pixelMatchesColor(cell_coordinates[0],
                                                    cell_coordinates[1],
                                                    (255, 0, 0),
                                                    tolerance=10)

            blue_pixel = pyautogui.pixelMatchesColor(cell_coordinates[0],
                                                     cell_coordinates[1],
                                                     (0, 0, 255),
                                                     tolerance=10)
                                                
            if red_pixel or blue_pixel:
                empty_cells_list.append(cell_coordinates)

        return empty_cells_list

    def __preparation_get_start_cell_color(self, 
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
            `list` of `dict` from `MapData`.
        start_cell_coords : Tuple[int, int]
            Starting cell's (x, y) coordinates.

        Returns
        ----------
        str
            Color of starting cell.

        """
        cells_list = self.__preparation_get_cells_from_database(
                map_coords,
                database,
            )

        index = cells_list.index(start_cell_coords)

        if index <= 1:
            return "red"
        elif index >= 2:
            return "blue"

    def __preparation_move_char_to_cell(self, cell_coordinates_list):
        """
        Move character to cell.

        Also saves the starting cell coordinates for use in "IN_COMBAT"
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
        # '__preparation_check_if_char_moved()' starts checking before 
        # character has time to move and gives false results.
        wait_after_move_char = 0.5

        for cell in cell_coordinates_list:
            print(f"[INFO] Moving character to cell: {cell} ... ")
            pyautogui.moveTo(cell[0], cell[1])
            pyautogui.click()
            self.__preparation_combat_start_cell_coords = cell
            time.sleep(wait_after_move_char)
            if self.__preparation_check_if_char_moved(cell):
                return True
        return False

    def __preparation_check_if_char_moved(self, cell_coordinates):
        """
        Check if character moved to cell.

        Checks for red and blue pixels on `cell_coordinates`. If
        neither are found it means character is standing there.
        
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
        red_pixel = pyautogui.pixelMatchesColor(cell_coordinates[0],
                                                cell_coordinates[1],
                                                (255, 0, 0),
                                                tolerance=5)
        blue_pixel = pyautogui.pixelMatchesColor(cell_coordinates[0],
                                                 cell_coordinates[1],
                                                 (0, 0, 255),
                                                 tolerance=5)

        if not red_pixel and not blue_pixel:
            print("[INFO] Character moved successfully!")
            return True
        else:
            print("[INFO] Failed to move character!")
            return False

    def __preparation_start_combat(self):
        """Click ready to start combat."""
        # Time to wait after clicking ready. How long to keep chacking 
        # if combat was started successfully.
        wait_combat_start = 10
        # 'Ready' button state.
        ready_button_clicked = False

        while True:

            screenshot = self.__window_capture.gamewindow_capture()
            ready_button_icon = self.__detection.get_click_coords(
                    self.__detection.find(
                            screenshot,
                            ImageData.s_i + ImageData.preparation_sv_2,
                            threshold=0.8
                        )
                    )

            # If 'READY' button was found.
            if len(ready_button_icon) > 0 and not ready_button_clicked:

                print("[INFO] Clicking 'READY' ... ")
                pyautogui.moveTo(x=ready_button_icon[0][0],
                                 y=ready_button_icon[0][1],
                                 duration=self.__move_duration)
                pyautogui.click()
                # Moving the mouse off the 'READY' button in case it 
                # needs to be detected again.
                pyautogui.move(0, 80)
                click_time = time.time()
                ready_button_clicked = True 

            # Checking if combat started after 'READY' was clicked.
            if ready_button_clicked:

                screenshot = self.__window_capture.gamewindow_capture()
                cc_icon = self.__detection.find(
                        screenshot,
                        ImageData.s_i + ImageData.in_combat_sv_1,
                        threshold=0.8
                    )
                ap_icon = self.__detection.find(
                        screenshot, 
                        ImageData.s_i + ImageData.in_combat_sv_2,
                        threshold=0.8
                    )
                mp_icon = self.__detection.find(
                        screenshot,
                        ImageData.s_i + ImageData.in_combat_sv_3,
                        threshold=0.8
                    )
                
                if time.time() - click_time > wait_combat_start:
                    print("[INFO] Failed to start combat!")
                    print("[INFO] Retrying ... ")
                    ready_button_clicked = False
                    continue

                if len(cc_icon) > 0 and len(ap_icon) > 0 and len(mp_icon) > 0:
                    print("[INFO] Successfully started combat!")
                    return True

    def __in_combat(self):
        """Combat state logic."""
        first_turn = True
        character_moved = False
        models_hidden = False
        tbar_shrunk = False

        while True:

            if self.__combat.turn_detect_start():

                if not tbar_shrunk:
                    if self.__combat.shrink_turn_bar():
                        tbar_shrunk = True

                if not models_hidden:
                    if self.__combat.hide_models():
                        models_hidden = True

                if not character_moved:
                    if self.__in_combat_move_character():
                        character_moved = True

                if character_moved and first_turn:
                    if self.__in_combat_cast_spells(first_turn=True):
                        if self.__combat.turn_pass():
                            print("[INFO] Waiting for turn ... ")
                            first_turn = False
                            continue

                elif character_moved and not first_turn:
                    if self.__in_combat_cast_spells(first_turn=False):
                        if self.__combat.turn_pass():
                            print("[INFO] Waiting for turn ... ")
                            continue

            elif self.__in_combat_detect_end_of_fight():
                self.__fight_counter += 1
                self.__total_fights += 1
                self.__state = BotState.CONTROLLER
                print(f"[INFO] Total fights: {self.__total_fights} ... ")
                break

    def __in_combat_move_character(self):
        """Move character."""
        attempts = 0
        attempts_allowed = 3

        while attempts < attempts_allowed:

            move_coords = self.__combat.get_movement_coordinates(
                    self.__map_coordinates,
                    self.__preparation_combat_start_cell_color,
                    self.__preparation_combat_start_cell_coords,
                )

            if self.__combat.get_if_char_on_correct_cell(move_coords):
                print("[INFO] Character is standing on correct cell!")
                # Moving mouse cursor off character so that spell bar
                # is visible and ready for detection.
                pyautogui.moveTo(x=609, y=752)
                return True

            else:
                print("[INFO] Moving character ... ")
                self.__combat.move_character(move_coords)

                start_time = time.time()
                wait_time = 3

                while time.time() - start_time < wait_time:
                    if self.__combat.get_if_char_on_correct_cell(move_coords):
                        pyautogui.moveTo(x=609, y=752)
                        return True
                else:
                    attempts += 1

        else:
            print(f"[ERROR] Failed to move character in '{attempts}' attempts!")
            print("[ERROR] Exiting ... ")
            os._exit(1)

    def __in_combat_cast_spells(self, first_turn):
        """
        Cast spells.
        
        Parameters
        ----------    
        first_turn : bool
            Whether it's the first turn of combat or not.
        
        """
        while True:

            available_spells = self.__combat.get_available_spells()

            if len(available_spells) <= 0:
                print("[INFO] No spells available!")
                return True

            for spell in available_spells:

                spell_coords = self.__combat.get_spell_coordinates(spell)

                if first_turn:
                    cast_coords = self.__combat.get_spell_cast_coordinates(
                            spell,
                            self.__map_coordinates,
                            self.__preparation_combat_start_cell_color,
                            self.__preparation_combat_start_cell_coords
                        )
                else:
                    cast_coords = self.__combat.get_char_position(
                            self.__preparation_combat_start_cell_color
                        )

                self.__combat.cast_spell(spell, spell_coords, cast_coords)
                break

    def __in_combat_detect_fight_results_window(self):
        """
        Detect close button of 'Fight Results' window.

        Returns
        ----------
        close_button : list[Tuple[int, int]]
            `list` of `tuple` containing [(x, y)] coordinates.

        """
        screenshot = self.__window_capture.gamewindow_capture()
        close_button = self.__detection.get_click_coords(
                self.__detection.find(
                        screenshot,
                        ImageData.s_i + ImageData.end_of_combat_v_1,
                        threshold=0.8
                    )
                )

        return close_button

    def __in_combat_detect_end_of_fight(self):
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

            close_button = self.__in_combat_detect_fight_results_window()

            if len(close_button) <= 0:
                return False

            elif len(close_button) > 0:

                print("[INFO] Combat has ended!")
                start_time = time.time()
                timeout_time = 10

                while time.time() - start_time < timeout_time:

                    print("[INFO] Closing 'Fight Results' window ... ")
                    # Separating mouse move and click actions, because
                    # otherwise it sometimes right clicks too early.
                    pyautogui.moveTo(x=close_button[0][0], 
                                     y=close_button[0][1], 
                                     duration=self.__move_duration)
                    pyautogui.click()
                    # Moving mouse off the 'Close' button in case it needs 
                    # to be detected again.
                    pyautogui.move(100, 0)

                    close_button = self.__in_combat_detect_fight_results_window()

                    if len(close_button) > 0:
                        print("[INFO] Failed to close 'Fight Results' window!")
                    elif len(close_button) <= 0:
                        print("[INFO] Successfully closed 'Fight Results' "
                              "window!")
                        # print("[INFO] Changing 'BotState' to: "
                        #       f"'{BotState.CONTROLLER}' ... ")
                        return True
                else:
                    print("[ERROR] Couldn't close 'Fight Results' window in "
                          f"{timeout_time} second(s)!")
                    print(f"[ERROR] Timed out!")
                    print(f"[ERROR] Exiting ... ")
                    os._exit(1)

    def __changing_map(self):
        """Changing map state logic."""
        attempts_total = 0
        attempts_allowed = 3

        while attempts_total < attempts_allowed:

            if self.__changing_map_change_map():
                self.__map_searched = False
                self.__state = BotState.CONTROLLER
                break
            else:
                if self.__popup.deal():
                    attempts_total += 1
                    continue

        else:
            print(f"[ERROR] Failed to change maps in {attempts_allowed} "
                  "attempts!")
            print("[ERROR] Exiting ... ")
            os._exit(1)

    def __changing_map_get_move_coords(self):
        """
        Get move (x, y) coordinates and move choice.

        Returns
        ----------
        move_coords : Tuple[int, int]
            (x, y) coordinates to click on for map change.
        move_choice : str
            Move direction.

        """
        # List of valid directions for moving.
        directions = ["top", "bottom", "left", "right"]

        # Get all possible moving directions from 'MapData'. 
        p_directions = []
        map_index = None
        for index, value in enumerate(self.__data_map):
            for i_key, i_value in value.items():
                if self.__map_coordinates == i_key:
                    for j_key, _ in i_value.items():
                        if j_key in directions:
                            p_directions.append(j_key)
                            map_index = index

        # Generating a random choice from gathered directions.
        move_choice = random.choice(p_directions)
  
        # Getting (x, y) coordinates.
        move_coords = self.__data_map[map_index]\
                                     [self.__map_coordinates]\
                                     [move_choice]

        return move_coords, move_choice

    def __changing_map_change_map(self):
        """
        Change maps.

        Logic
        ----------
        - Get coordinates on yellow sun to click on to change maps.
        - Click.
        - Checks if map was changed successfully.
            - If changed successfully - return `True`.
            - If failed to change - return `False`.

        Returns
        ----------
        True : bool
            If map change was a success.
        False : bool
            If map change was unsuccessful.

        """
        # How long to keep checking if map was changed.
        wait_change_map = 7
        # Time to wait before clicking on yellow 'sun' to change maps.
        # Must wait when moving in 'bottom' direction, because 'Dofus' 
        # GUI blocks the sun otherwise.
        wait_bottom_click = 0.5

        # Changing maps.
        coords, choice = self.__changing_map_get_move_coords()
        print(f"[INFO] Clicking on: {(coords[0], coords[1])} to move "
                f"'{choice}' ... ")
        pyautogui.keyDown('e')
        pyautogui.moveTo(coords[0], coords[1])
        if choice == "bottom":
            time.sleep(wait_bottom_click)
        pyautogui.click()
        pyautogui.keyUp('e')

        # Checking if map was changed.
        start_time = time.time()
        sc_mm = self.__changing_map_screenshot_minimap()
        
        while time.time() - start_time < wait_change_map:
            if self.__changing_map_detect_if_map_changed(sc_mm):
                return True
        else:
            print("[INFO] Failed to change maps!")
            return False

    def __changing_map_screenshot_minimap(self):
        """
        Get screenshot of coordinates on minimap.

        Used in '__changing_map_change_map()' when checking if map was
        changed successfully.
        
        Returns
        ----------
        screenshot : np.ndarray
            Screenshot of coordinates on the minimap.

        """
        # Moving mouse over the red area on the minimap for the black 
        # map tooltip to appear.
        pyautogui.moveTo(517, 680)
        # Waiting makes overall performance better because of less
        # screenshots.
        time.sleep(0.25)
        screenshot = self.__window_capture.custom_area_capture(
                capture_region=self.__window_capture.MAP_DETECTION_REGION,
                conversion_code=cv.COLOR_RGB2GRAY,
                interpolation_flag=cv.INTER_LINEAR,
                scale_width=100,
                scale_height=100
            )
        # Moving mouse off the red area on the minimap in case a new 
        # screenshot is required for another detection.
        pyautogui.move(20, 0)

        return screenshot

    def __changing_map_detect_if_map_changed(self, sc_minimap):
        """
        Check if map was changed successfully.

        Logic
        ----------
        - Take screenshot of minimap.
        - Compare `sc_minimap` against locally taken screenshot of 
        minimap.
            - If images are different, means map changed succesfully - 
            return `True`.

        Parameters
        ----------
        sc_minimap : np.ndarray
            Screenshot of minimap.

        Returns
        ----------
        True : bool
            If map was changed successfully.

        """
        # Time to wait for map to load after a successful map change. 
        # Determines how long script will wait after character moves to 
        # a new map. The lower the number, the higher the chance that on 
        # a slower machine 'SEARCHING' state will act too fast & try to 
        # search for monsters on a black "LOADING MAP" screen. This wait 
        # time allows the black loading screen to disappear.
        wait_map_loading = 0.5

        sc_minimap_needle = self.__changing_map_screenshot_minimap()
        minimap_rects = self.__detection.find(sc_minimap,
                                              sc_minimap_needle,
                                              threshold=0.99)

        # If screenshots are different.
        if len(minimap_rects) <= 0:
            time.sleep(wait_map_loading)
            print("[INFO] Map changed successfully!")
            return True

    def __banking(self):
        """
        Banking logic.

        Logic
        ----------
        - If on "4,-16" map.
            - Close any pop-ups & interfaces.
            - Detect if inside or outside Astrub bank.
                - If not inside - move character inside.
                - Elif inside and items have been deposited - move
                character outside.
                - Elif inside ant items have not been deposited - open
                bank, deposit items and close bank.
        - Else:
            - Change 'BotState' to 'CHANGING_MAP'.

        Program will exit if: 
            - `attempts_total` < `attempts_allowed`.
            - `timeout` seconds reached.

        """
        while True:

            if self.__map_coordinates == "4,-16":

                attempts_total = 0
                attempts_allowed = 5
                items_deposited = False

                while attempts_total < attempts_allowed:

                    self.__popup.deal()
                    character_inside_bank = self.__bank.inside_or_outside()

                    if not character_inside_bank:
                        if self.__bank.enter_bank():
                            continue
                        else:
                            attempts_total += 1

                    elif character_inside_bank and items_deposited:
                        if self.__bank.exit_bank():
                            self.__fight_counter = 0
                            self.__state = BotState.CONTROLLER
                            return
                        else:
                            attempts_total += 1
                            continue
                        
                    elif character_inside_bank and not items_deposited:

                        start_time = time.time()
                        timeout = 60

                        while time.time() - start_time < timeout:
                            self.__popup.deal()
                            if self.__bank.open_bank_vault():
                                if self.__bank.deposit_items():
                                    if self.__bank.close_bank_vault():
                                        items_deposited = True
                                        break

                        else:
                            print("[ERROR] Failed to complete actions inside "
                                  f"bank in {timeout} seconds!")
                            print("[ERROR] Timed out ... ")
                            print("[ERROR] Exiting ... ")
                            os._exit(1)

                else:
                    print("[ERROR] Failed to enter/exit bank in "
                          f"{attempts_allowed} attempts!")
                    print("[ERROR] Exiting ... ")
                    os._exit(1)

            else:
                self.__state = BotState.CHANGING_MAP
                break

#----------------------------------------------------------------------#
#------------------------MAIN THREAD OF CONTROL------------------------#
#----------------------------------------------------------------------#

    def __Bot_Thread_run(self):
        """Execute this code while bot thread is alive."""
        while not self.__Bot_Thread_stopped:

            # The bot always starts up in this (INITIALIZING) state. 
            if self.__state == BotState.INITIALIZING:
                self.__initializing()

            # Determines what state to switch to when out of combat.
            elif self.__state == BotState.CONTROLLER:
                self.__controller()

            # Handles monster detection.
            elif self.__state == BotState.SEARCHING:
                self.__searching()

            # Handles attacking found monsters.
            elif self.__state == BotState.ATTACKING:
                self.__attacking()

            # Handles combat preparation actions.
            elif self.__state == BotState.PREPARATION:
                self.__preparation()

            # Handles combat actions.
            elif self.__state == BotState.IN_COMBAT:
                self.__in_combat()
                        
            # Handles map changing actions.
            elif self.__state == BotState.CHANGING_MAP:
                self.__changing_map()

            # Handles banking.
            elif self.__state == BotState.BANKING:
                self.__banking()

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
        self.__threading_tools.wait_thread_start(self.__Bot_Thread_thread)

    def Bot_Thread_stop(self):
        """Stop bot thread."""
        self.__Bot_Thread_stopped = True
        self.__VisualDebugWindow_Thread_stop()
        self.__threading_tools.wait_thread_stop(self.__Bot_Thread_thread)

#----------------------------------------------------------------------#

    def __VisualDebugWindow_Thread_start(self):
        """Start VisualDebugOutput thread."""
        self.__VisualDebugWindow_Thread_stopped = False
        self.__VisualDebugWindow_Thread_thread = threading.Thread(
                target=self.__VisualDebugWindow_Thread_run
            )
        self.__VisualDebugWindow_Thread_thread.start()
        self.__threading_tools.wait_thread_start(
                self.__VisualDebugWindow_Thread_thread
            )

    def __VisualDebugWindow_Thread_stop(self):
        """Stop VisualDebugOutput thread."""
        self.__VisualDebugWindow_Thread_stopped = True
        self.__threading_tools.wait_thread_stop(
                self.__VisualDebugWindow_Thread_thread
            )
        
    def __VisualDebugWindow_Thread_run(self):
        """Execute this code while thread is alive."""
        start_time = time.time()
        counter = 0
        fps = 0

        while not self.__VisualDebugWindow_Thread_stopped:

            # Get screenshot of game.
            screenshot = self.__window_capture.gamewindow_capture()

            # Draw boxes around detected monsters.
            output_image = self.__detection.draw_rectangles(
                    screenshot,
                    self.__obj_rects
                )

            # Calculating and displaying debug output FPS.
            output_image = cv.putText(img=output_image,
                                      text=f"Debug Window FPS: {fps}",
                                      org=(0, 70),
                                      fontFace=cv.FONT_HERSHEY_PLAIN,
                                      fontScale=1,
                                      color=(0, 255, 255),
                                      thickness=2)

            # Press 'q' while the DEBUG window is focused to exit.
            # Force killing all threads (not clean).
            cv.imshow("Visual Debug Window", output_image)
            if cv.waitKey(1) == ord("q"):
                cv.destroyAllWindows()
                print("Done")
                os._exit(1)

            counter += 1
            if (time.time() - start_time) > 1:
                fps = round(counter / (time.time() - start_time))
                start_time = time.time()
                counter = 0

#----------------------------------------------------------------------#

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
import threading_tools as tt
import window_capture as wc


class BotState:
    """Bot states enum."""

    INITIALIZING = "INITIALIZING"
    CONTROLLER = "CONTROLLER"
    HUNTING = "HUNTING"
    PREPARING = "PREPARING"
    FIGHTING = "FIGHTING"
    MOVING = "MOVING"
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
    # 'Window_VisualDebugOutput_Thread' threading attributes.
    __VisualDebugWindow_Thread_stopped = True
    __VisualDebugWindow_Thread_thread = None

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

    # 'BotState.HUNTING'.
    # Bounding box information and coordinates of detected monsters.
    __obj_rects = []
    __obj_coords = []

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
        self.__script = script
        self.__character_name = character_name
        self.__official_version = official_version
        self.__debug_window = debug_window
        self.__state = bot_state

        gw.GameWindow.character_name = character_name
        gw.GameWindow.official_version = official_version
        cbt.Combat.character_name = character_name
        bank.Bank.official_version = official_version

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

    def __get_coordinates(self, map_database):
        """
        Get current map's coordinates.

        Parameters
        ----------
        map_database : list[dict]
            Map's database.
        
        Returns
        ----------
        coords : str
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
        timeout = 7

        while time.time() - start_time < timeout:

            # Checking for offers/interfaces and closing them.
            pu.PopUp.deal()

            # Get a screenshot of coordinates on minimap. Moving mouse
            # over the red area on the minimap for the black map tooltip
            # to appear.
            pyautogui.moveTo(517, 680)
            time.sleep(wait_before_detecting)
            screenshot = wc.WindowCapture.custom_area_capture(
                    capture_region=(525, 650, 45, 30),
                    conversion_code=cv.COLOR_RGB2GRAY,
                    interpolation_flag=cv.INTER_LINEAR,
                    scale_width=160,
                    scale_height=200
                )
            # Moving mouse off the red area on the minimap in case a new 
            # screenshot is required for another detection.
            pyautogui.move(20, 0)

            # Get map coordinates as a string.
            r_and_t, _, _ = dtc.Detection.detect_text_from_image(screenshot)
            try:
                coords = r_and_t[0][1]
                coords = coords.replace(".", ",")
                coords = coords.replace(" ", "")
                # Inserting ',' if it wasn't detected before second '-'.
                if "-" in coords:
                    index = coords.rfind("-")
                    if index != 0:
                        if coords[index-1].isdigit():
                            coords = coords[:index] + "," + coords[index:]
            except IndexError:
                continue

            if self.__check_if_map_in_database(coords, map_database):
                return coords
            else:
                log.error(f"Map ({coords}) doesn't exist in database!")
                self.__recovery_emergency_teleport()

        else:
            log.error("Error in '__get_coordinates()'!")
            log.error(f"Exceeded detection limit of {timeout} second(s)!")
            self.__recovery_emergency_teleport()

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
        """'INITIALIZING' state logic."""
        # Making sure 'Dofus.exe' is launched and char is logged in.
        if gw.GameWindow.check_if_exists():
            gw.GameWindow.resize_and_move()
        else:
            os._exit(1)

        # Starts 'Window_VisualDebugOutput_Thread' if needed.
        if self.__debug_window:
            self.__VisualDebugWindow_Thread_start()

        # Loading bot script data.
        if self.__initializing_load_bot_script_data(self.__script):
            log.info(f"Successfully loaded '{self.__script}' script!")

        if self.__official_version:
            if self.__initializing_verify_group():
                log.info("Group verified successfully!")

        if self.__initializing_verify_character_name(self.__character_name):
            log.info("Character's name set correctly!")

        # Passing control to 'CONTROLLER' state.
        log.info(f"Changing 'BotState' to: '{BotState.CONTROLLER}' ... ")
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
            log.critical("Parameter 'script' must be a string!")
            log.critical("Exiting ... ")
            os._exit(1)

        script = script.lower()

        if script == "af_anticlock":
            self.__data_map_hunting = data.scripts.af_anticlock.Hunting.data
            self.__data_map_banking = data.scripts.af_anticlock.Banking.data
            self.__data_monsters = dtc.Detection.generate_image_data(
                    data.images.monster.AstrubForest.img_list,
                    data.images.monster.AstrubForest.img_path
                )
            # self.__data_monsters = dtc.Detection.generate_image_data(
            #         image_list=["test_1.png"],
            #         image_path="data\\images\\test\\monster_images\\"
            #     )
            cbt.Combat.data_spell_cast = data.scripts.af_anticlock.Cast.data
            cbt.Combat.data_movement = data.scripts.af_anticlock.Movement.data
            bank.Bank.img_path = data.images.npc.AstrubBanker.img_path
            bank.Bank.img_list = data.images.npc.AstrubBanker.img_list
            self.__script = "Astrub Forest - Anticlock"
            return True

        elif script == "af_clockwise":
            self.__data_map_hunting = data.scripts.af_clockwise.Hunting.data
            self.__data_map_banking = data.scripts.af_clockwise.Banking.data
            self.__data_monsters = dtc.Detection.generate_image_data(
                    data.images.monster.AstrubForest.img_list,
                    data.images.monster.AstrubForest.img_path
                )
            cbt.Combat.data_spell_cast = data.scripts.af_clockwise.Cast.data
            cbt.Combat.data_movement = data.scripts.af_clockwise.Movement.data
            bank.Bank.img_path = data.images.npc.AstrubBanker.img_path
            bank.Bank.img_list = data.images.npc.AstrubBanker.img_list
            self.__script = "Astrub Forest - Clockwise"
            return True

        else:
            log.critical(f"Couldn't find script '{script}' in database!")
            log.critical("Exiting ... ")
            os._exit(1)

    def __initializing_verify_character_name(self, character_name):
        """
        Check if name in characteristics interface matches one that's
        passed in during script startup.

        character_name : str
            Character's name.

        Returns
        ----------
        True : bool
            If names match.
        NoReturn
            Program will exit if names do not match or characteristics
            interface couldn't be opened `attempts_allowed` times.
        
        """
        log.info("Verifying character's name ... ")

        attempts_allowed = 3
        attempts_total = 0

        while attempts_total < attempts_allowed:

            pu.PopUp.deal()

            if pu.PopUp.interface("characteristics", "open"):

                sc = wc.WindowCapture.custom_area_capture((685, 93, 205, 26))
                r_and_t, _, _ = dtc.Detection.detect_text_from_image(sc)
                detected_name = r_and_t[0][1]

                if character_name == detected_name:
                    pu.PopUp.interface("characteristics", "close")
                    return True
                else:
                    log.critical("Invalid character name!")
                    log.critical("Exiting ... ")
                    os._exit(1)

            else:
                attempts_total += 1
        
        else:
            log.critical("Failed to open characteristics interface "
                         f"{attempts_allowed} times!")
            log.critical("Exiting ... ")
            wc.WindowCapture.on_exit_capture()

    def __initializing_verify_group(self):
        """Check if character is in group and close group tab."""
        log.info("Verifying group ... ")

        start_time = time.time()
        timeout = 15

        while time.time() - start_time < timeout:

            if self.__initializing_in_group():
                log.info("Character is in group!")
                if self.__initializing_group_tab_check() == "opened":
                    if self.__initializing_group_tab_hide():
                        return True
                else:
                    return True

        else:
            log.critical(f"Failed to verify group in {timeout} seconds!")
            log.critical(f"Exiting ... ")
            wc.WindowCapture.on_exit_capture()

    def __initializing_in_group(self):
        """Check if character is in group."""
        coords = [(908, 120), (913, 115), (902, 117)]
        colors = [(0, 153, 0), (0, 138, 0)]
        pixels = []

        for coord in coords:
            for color in colors:
                px = pyautogui.pixelMatchesColor(coord[0], coord[1], color)
                pixels.append(px)

        if pixels.count(True) == len(coords):
            return True
        else:
            return False  

    def __initializing_group_tab_check(self):
        """Check if group tab is opened or closed."""
        coords = [(908, 142), (910, 138), (915, 142)]
        colors = [(197, 73, 6), (102, 45, 23), (103, 32, 5)]
        pixels = []

        for i in range(len(colors)):
            px = pyautogui.pixelMatchesColor(coords[i][0], coords[i][1], colors[i])
            pixels.append(px)

        if all(pixels):
            return "opened"
        else:
            return "closed"

    def __initializing_group_tab_hide(self):
        """Hide group tab if it's open."""
        start_time = time.time()
        timeout = 30

        while time.time() - start_time < timeout:

            pu.PopUp.deal()

            if self.__initializing_group_tab_check() == "opened":
                log.info("Hiding group tab ... ")
                pyautogui.moveTo(927, 117, duration=0.15)
                pyautogui.click()
                time.sleep(0.5)
            else:
                log.info("Group tab hidden successfully!")
                return True

        else:
            log.critical(f"Failed to hide group tab in {timeout} seconds!")
            log.critical(f"Exiting ... ")
            wc.WindowCapture.on_exit_capture()

    def __controller(self):
        """Set bot state according to situation."""

        if self.__official_version:
            pu.PopUp.close_right_click_menu()
            if not self.__initializing_in_group():
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
            self.__map_coords = self.__get_coordinates(self.__data_map)
            self.__state = BotState.BANKING

        elif not self.__character_overloaded:
            self.__data_map = self.__data_map_hunting
            self.__map_coords = self.__get_coordinates(self.__data_map)
            map_type = self.__get_map_type(self.__map_coords)

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

    def __hunting(self):
        """'HUNTING' state logic."""
        log.info(f"Hunting on map ({self.__map_coords}) ... ")

        chunks = self.__hunting_chunkate_data(
                image_list=list(self.__data_monsters.keys()),
                chunk_size=4
            )

        for chunk_number, chunk in chunks.items():

            self.__obj_rects, self.__obj_coords = self.__hunting_search(
                    image_data=self.__data_monsters,
                    image_list=chunk
                )

            if len(self.__obj_coords) > 0:

                attack = self.__hunting_attack(self.__obj_coords)

                if attack == "success":
                    self.__state = BotState.PREPARING
                    break

                elif attack == "map_change":
                    self.__state = BotState.CONTROLLER
                    break
                
            if chunk_number + 1 == len(chunks.keys()):
                log.info(f"Map ({self.__map_coords}) is clear!")
                self.__map_searched = True
                self.__state = BotState.CONTROLLER

    def __hunting_chunkate_data(self, image_list, chunk_size):
        """
        Split monster image list into equally sized chunks.
        
        Parameters
        ----------
        image_list : list[str]
            `list` of `str` containing names of image files.
        chunk_size : int
            Amount of images to put in a chunk.

        Returns
        ----------
        chunkated_data : dict[int: list[str]]
            `image_list` split into equal `chunk_size` chunks. Last
            chunk won't have `chunk_size` images if len(`image_list`) %
            `chunk_size` != 0.

        """
        total_images = len(image_list)

        chunkated_data = []
        for i in range(0, total_images, chunk_size):
            chunk = image_list[i:i+chunk_size]
            chunkated_data.append(chunk)

        chunkated_data = {k: v for k, v in enumerate(chunkated_data)}

        return chunkated_data

    def __hunting_search(self, image_data, image_list):
        """
        Search for monsters.
        
        Parameters
        ----------
        image_data : dict[str: Tuple[np.ndarray, np.ndarray]]
            Dictionary containing image information. Can be generated by
            `generate_image_data()` method.
        image_list : list[str]
            `list` of images to search for. These images are used as
            keys to access data in `image_data`.

        Returns
        ----------
        obj_rects : list[list[int]]
            2D `list` containing [[topLeft_x, topLeft_y, width, height]] 
            of bounding box.
        obj_coords : list[Tuple[int, int]]
            `list` of `tuple` containing [(x, y)] coordinates.
        obj_rects : tuple
            Empty `tuple` if no matches found.
        obj_coords : list
            Empty `list` if no matches found.

        """
        # Moving mouse of the screen so it doesn't hightlight mobs
        # by accident causing them to be undetectable.
        pu.PopUp.close_right_click_menu()

        screenshot = wc.WindowCapture.gamewindow_capture()
        obj_rects, obj_coords = dtc.Detection.detect_objects_with_masks(
                image_data,
                image_list,
                screenshot,
            )

        if len(obj_coords) > 0:
            log.info(f"Monsters found at: {obj_coords}!")
            return obj_rects, obj_coords

        return obj_rects, obj_coords

    def __hunting_attack(self, monster_coords):
        """
        Attack monsters.

        Parameters
        ----------
        monster_coords : list[Tuple[int, int]]
            Monster coordinates.
        
        Returns
        ----------
        True : bool
            If monster was attacked successfully.
        False : bool
            If failed to attack monster `attempts_allowed` times.
        
        """
        wait_after_attacking = 6
        attempts_allowed = 1
        attempts_total = 0

        if len(monster_coords) < attempts_allowed:
            attempts_allowed = len(monster_coords)

        for i in range(0, attempts_allowed):

            pu.PopUp.deal()
            scs_before_attack = self.__moving_screenshot_minimap()

            x, y = monster_coords[i]
            log.info(f"Attacking monster at: {x, y} ... ")
            pyautogui.moveTo(x, y, duration=0.15)
            pyautogui.click(button="right")

            if self.__hunting_check_right_click_menu():
                log.info(f"Failed to attack monster at: {x, y}!")
                return "right_click_menu"
            
            attack_time = time.time()
            while time.time() - attack_time < wait_after_attacking:

                screenshot = wc.WindowCapture.gamewindow_capture()
                cc_icon = dtc.Detection.find(
                        screenshot,
                        data.images.Status.preparing_sv_1
                    )
                ready_button = dtc.Detection.find(
                        screenshot,
                        data.images.Status.preparing_sv_2
                    )
                
                if len(cc_icon) > 0 and len(ready_button) > 0:
                    log.info(f"Successfully attacked monster at: {x, y}!")
                    return "success"

            else:

                log.info(f"Failed to attack monster at: {x, y}!")
                attempts_total += 1

                if self.__hunting_accidental_map_change(scs_before_attack):
                    return "map_change"

                if (attempts_allowed == attempts_total):
                    return "fail"

    def __hunting_accidental_map_change(self, sc_before_attack):
        """Check if map was changed accidentally during an attack."""
        sc_after_attack = self.__moving_screenshot_minimap()
        rects = dtc.Detection.find(sc_before_attack, 
                                   sc_after_attack,
                                   threshold=0.98)
        if len(rects) <= 0:
            log.info("Map was changed accidentally during an attack!")
            return True

    def __hunting_check_right_click_menu(self):
        """Check if right click menu is open."""
        # Allowing the menu to appear before taking a screnshot.
        time.sleep(0.5)
        sc = wc.WindowCapture.gamewindow_capture()
        rects = dtc.Detection.find(sc, 
                                   data.images.Interface.right_click_menu,
                                   threshold=0.7)
        if len(rects) > 0:
            return True
        else:
            return False

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
                self.__map_coords = self.__get_coordinates(self.__data_map)
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
                    self.__map_coords = self.__get_coordinates(self.__data_map)
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
                self.__map_coords = self.__get_coordinates(self.__data_map)
                continue

            if self.__preparing_move_char_to_cell(e_cells):
                log.info("Successfully moved character to dummy cell!")
                return True

            else:

                if failed_attempts < attempts_allowed:
                    self.__map_coords = self.__get_coordinates(self.__data_map)
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

    def __moving(self):
        """'MOVING' state logic."""
        attempts_total = 0
        attempts_allowed = 5

        while attempts_total < attempts_allowed:

            if self.__moving_change_map():
                self.__map_searched = False
                self.__state = BotState.CONTROLLER
                # Resetting emergency teleport count to 0 after a
                # successful map change. Means character is not stuck
                # and good to go.
                self.__emergency_teleports = 0
                break
            else:
                pu.PopUp.deal()
                attempts_total += 1

                if self.__map_coords == "1,-25":
                    if self.__moving_detect_lumberjack_ws_interior():
                        pyautogui.keyDown('e')
                        pyautogui.moveTo(667, 507)
                        pyautogui.click()
                        pyautogui.keyUp('e')
                        time.sleep(3)
                    
                self.__map_coords = self.__get_coordinates(
                            self.__data_map
                        )
                continue

        else:
            log.error(f"Failed to change maps in {attempts_allowed} "
                      "attempts!")
            self.__recovery_emergency_teleport()

    def __moving_detect_lumberjack_ws_interior(self):
        """Detect if character is inside lumberjack's workshop."""
        color = (0, 0, 0)
        coordinates = [(49, 559), (48, 137), (782, 89), (820, 380), (731, 554)]

        pixels = []
        for coord in coordinates:
            px = pyautogui.pixelMatchesColor(coord[0], coord[1], color)
            pixels.append(px)

        if all(pixels):
            log.info("Character is inside 'Lumberjack's Workshop'!")
            return True
        else:
            return False

    def __moving_get_move_coords(self):
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

        # Get all possible moving directions from loaded map data. 
        p_directions = []
        map_index = None
        for index, value in enumerate(self.__data_map):
            for i_key, i_value in value.items():
                if self.__map_coords == i_key:
                    for j_key, _ in i_value.items():
                        if j_key in directions:
                            p_directions.append(j_key)
                            map_index = index

        # Generating a random choice from gathered directions.
        move_choice = random.choice(p_directions)
  
        # Getting (x, y) coordinates.
        move_coords = self.__data_map[map_index]\
                                     [self.__map_coords]\
                                     [move_choice]

        return move_coords, move_choice

    def __moving_change_map(self):
        """
        Change maps.

        Logic
        ----------
        - Get coordinates on yellow sun to click on to change maps.
        - Click.
        - Checks if map was changed successfully.
            - If changed successfully: 
                - Return `True`.
            - If failed to change:
                - Return `False`.

        Returns
        ----------
        True : bool
            If map change was a success.
        False : bool
            If map change was unsuccessful.

        """
        # How long to keep checking if map was changed.
        wait_change_map = 9
        # Time to wait before clicking on yellow 'sun' to change maps.
        # Must wait when moving in 'bottom' direction, because 'Dofus' 
        # GUI blocks the sun otherwise.
        wait_bottom_click = 0.5

        # Changing maps.
        pu.PopUp.close_right_click_menu()
        coords, choice = self.__moving_get_move_coords()
        log.info(f"Clicking on: {coords[0], coords[1]} to move {choice} ... ")
        pyautogui.keyDown('e')
        pyautogui.moveTo(coords[0], coords[1])
        if choice == "bottom":
            time.sleep(wait_bottom_click)
        pyautogui.click()
        pyautogui.keyUp('e')

        # Checking if map was changed.
        start_time = time.time()
        sc_mm = self.__moving_screenshot_minimap()
        
        while time.time() - start_time < wait_change_map:
            if self.__moving_detect_if_map_changed(sc_mm):
                return True
        else:
            log.error("Failed to change maps!")
            return False

    def __moving_screenshot_minimap(self):
        """
        Get screenshot of coordinates on minimap.

        Used in '__moving_change_map()' when checking if map was
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
        # screenshots. Also gives time for map tooltip to appear.
        time.sleep(0.5)
        screenshot = wc.WindowCapture.custom_area_capture(
                capture_region=(525, 650, 45, 30),
                conversion_code=cv.COLOR_RGB2GRAY,
                interpolation_flag=cv.INTER_LINEAR,
                scale_width=100,
                scale_height=100
            )
        # Moving mouse off the red area on the minimap in case a new 
        # screenshot is required for another detection.
        pyautogui.move(20, 0)

        return screenshot

    def __moving_detect_if_map_changed(self, sc_minimap):
        """
        Check if map was changed successfully.

        Logic
        ----------
        - Take screenshot of minimap.
        - Compare `sc_minimap` against locally taken screenshot of 
        minimap.
        - If images are different, means map changed succesfully:
            - Return `True`.

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
        wait_map_loading = 1
        sc_minimap_needle = self.__moving_screenshot_minimap()
        minimap_rects = dtc.Detection.find(sc_minimap,
                                           sc_minimap_needle,
                                           threshold=0.99)

        # If screenshots are different.
        if len(minimap_rects) <= 0:
            time.sleep(wait_map_loading)
            log.info("Map changed successfully!")
            return True

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
            self.__map_coords = self.__get_coordinates(
                    self.__data_map
                )

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

    def __recovery_emergency_teleport(self):
        """Teleport using 'Recall Potion' when stuck somewhere."""

        log.debug(f"Emergency teleports: {self.__emergency_teleports}")
        pu.PopUp.deal()

        if self.__emergency_teleports >= 3:
            log.info(f"Emergency teleport limit exceeded!")
            log.info(f"Exiting ... ")
            wc.WindowCapture.on_exit_capture()
        elif bank.Bank.recall_potion() == "available":
            self.__emergency_teleports += 1
            self.__banking_use_recall_potion()
        else:
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
                    self.__initializing()

                # Determines what state to switch to when out of combat.
                elif self.__state == BotState.CONTROLLER:
                    self.__controller()

                # Handles detection and attacking of monsters.
                elif self.__state == BotState.HUNTING:
                    self.__hunting()

                # Handles combat preparation.
                elif self.__state == BotState.PREPARING:
                    self.__preparing()

                # Handles combat.
                elif self.__state == BotState.FIGHTING:
                    self.__fighting()
                            
                # Handles map changing.
                elif self.__state == BotState.MOVING:
                    self.__moving()

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

    def __VisualDebugWindow_Thread_start(self):
        """Start VisualDebugOutput thread."""
        self.__VisualDebugWindow_Thread_stopped = False
        self.__VisualDebugWindow_Thread_thread = threading.Thread(
                target=self.__VisualDebugWindow_Thread_run
            )
        self.__VisualDebugWindow_Thread_thread.start()
        tt.ThreadingTools.wait_thread_start(
                self.__VisualDebugWindow_Thread_thread
            )

    def __VisualDebugWindow_Thread_stop(self):
        """Stop VisualDebugOutput thread."""
        self.__VisualDebugWindow_Thread_stopped = True
        
    def __VisualDebugWindow_Thread_run(self):
        """Execute this code while thread is alive."""
        start_time = time.time()
        counter = 0
        fps = 0

        while not self.__VisualDebugWindow_Thread_stopped:

            # Get screenshot of game.
            screenshot = wc.WindowCapture.gamewindow_capture()

            # Draw boxes around detected monsters.
            output_image = dtc.Detection.draw_rectangles(
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
                os._exit(1)

            counter += 1
            if (time.time() - start_time) > 1:
                fps = round(counter / (time.time() - start_time))
                start_time = time.time()
                counter = 0

#----------------------------------------------------------------------#

"""Logic related to 'MOVING' bot state."""

from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True)

import random
import time

import cv2 as cv
import pyautogui as pyag

import bank
from .botstate_enum import BotState
import detection as dtc
import pop_up as pu
import window_capture as wc


class Moving:
    """Holds various 'MOVING' state methods."""

    # Public class attributes.
    emergency_teleports = 0
    map_coords = None
    data_map = None
    state = None
    map_searched = None


    @classmethod
    def moving(cls):
        """'MOVING' state logic."""
        attempts_total = 0
        attempts_allowed = 5

        while attempts_total < attempts_allowed:

            if cls.__change_map(cls.data_map, cls.map_coords):
                cls.map_searched = False
                cls.state = BotState.CONTROLLER
                # Resetting emergency teleport count to 0 after a
                # successful map change. Means character is not stuck
                # and good to go.
                cls.emergency_teleports = 0
                return cls.state, cls.map_searched

            else:

                pu.PopUp.deal()
                attempts_total += 1

                if cls.map_coords == "1,-25":
                    if cls.__detect_lumberjack_ws_interior():
                        pyag.keyDown('e')
                        pyag.moveTo(667, 507)
                        pyag.click()
                        pyag.keyUp('e')
                        time.sleep(3)
                    
                cls.map_coords = cls.get_coordinates(cls.data_map)
                continue

        else:
            log.error(f"Failed to change maps in {attempts_allowed} "
                      "attempts!")
            cls.__recovery_emergency_teleport()

    @classmethod
    def get_coordinates(cls, database):
        """
        Get current map's coordinates.

        Parameters
        ----------
        database : list[dict]
            Map database.
        
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
            pyag.moveTo(517, 680)
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
            pyag.move(20, 0)

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

            if cls.__check_if_map_in_database(coords, database):
                return coords
            else:
                log.error(f"Map ({coords}) doesn't exist in database!")
                cls.__recovery_emergency_teleport()

        else:
            log.error("Error in 'get_coordinates()'!")
            log.error(f"Exceeded detection limit of {timeout} second(s)!")
            cls.__recovery_emergency_teleport()

    @classmethod
    def get_map_type(cls, database, map_coordinates):
        """
        Get current map's type.
        
        Parameters
        ----------
        database : list[dict]
            Map database.
        map_coordinates : str
            Current map's coordinates.

        Returns
        ----------
        map_type : str
            Current map's type.
        
        """
        for _, value in enumerate(database):
            for i_key, i_value in value.items():
                if map_coordinates == i_key:
                    map_type = i_value["map_type"]
                    return map_type

    @staticmethod
    def screenshot_minimap():
        """
        Get screenshot of coordinates on minimap.

        Used in '__change_map()' when checking if map was
        changed successfully.
        
        Returns
        ----------
        screenshot : np.ndarray
            Screenshot of coordinates on the minimap.

        """
        # Moving mouse over the red area on the minimap for the black 
        # map tooltip to appear.
        pyag.moveTo(517, 680)
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
        pyag.move(20, 0)

        return screenshot

    @classmethod
    def __detect_if_map_changed(cls, sc_minimap):
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
        sc_minimap_needle = cls.screenshot_minimap()
        minimap_rects = dtc.Detection.find(sc_minimap,
                                           sc_minimap_needle,
                                           threshold=0.99)

        # If screenshots are different.
        if len(minimap_rects) <= 0:
            time.sleep(wait_map_loading)
            log.info("Map changed successfully!")
            return True

    @classmethod
    def __change_map(cls, database, map_coords):
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

        Parameters
        ----------
        database : list[dict]
            Map database.
        map_coords : str
            Map coordinates.

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
        coords, choice = cls.__get_move_coords(database, map_coords)
        log.info(f"Clicking on: {coords[0], coords[1]} to move {choice} ... ")
        pyag.keyDown('e')
        pyag.moveTo(coords[0], coords[1])
        if choice == "bottom":
            time.sleep(wait_bottom_click)
        pyag.click()
        pyag.keyUp('e')

        # Checking if map was changed.
        start_time = time.time()
        sc_mm = cls.screenshot_minimap()
        
        while time.time() - start_time < wait_change_map:
            if cls.__detect_if_map_changed(sc_mm):
                return True
        else:
            log.error("Failed to change maps!")
            return False

    @classmethod
    def __recovery_emergency_teleport(cls):
        """Teleport using 'Recall Potion' when stuck somewhere."""

        log.debug(f"Emergency teleports: {cls.emergency_teleports}")
        pu.PopUp.deal()

        if cls.emergency_teleports >= 3:
            log.info(f"Emergency teleport limit exceeded!")
            log.info(f"Exiting ... ")
            wc.WindowCapture.on_exit_capture()
        # elif bank.Bank.recall_potion() == "available":
        #     cls.emergency_teleports += 1
        #     cls.__banking_use_recall_potion()
        # else:
        #     wc.WindowCapture.on_exit_capture()

    @staticmethod
    def __detect_lumberjack_ws_interior():
        """Detect if character is inside lumberjack's workshop."""
        color = (0, 0, 0)
        coordinates = [(49, 559), (48, 137), (782, 89), (820, 380), (731, 554)]

        pixels = []
        for coord in coordinates:
            px = pyag.pixelMatchesColor(coord[0], coord[1], color)
            pixels.append(px)

        if all(pixels):
            log.info("Character is inside 'Lumberjack's Workshop'!")
            return True
        else:
            return False

    @staticmethod
    def __get_move_coords(database, map_coords):
        """
        Get move (x, y) coordinates and move choice.

        Parameters
        ----------
        database : list[dict]
            Map database. 
        map_coords : str
            Map coordinates.

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
        for index, value in enumerate(database):
            for i_key, i_value in value.items():
                if map_coords == i_key:
                    for j_key, _ in i_value.items():
                        if j_key in directions:
                            p_directions.append(j_key)
                            map_index = index

        # Generating a random choice from gathered directions.
        move_choice = random.choice(p_directions)
  
        # Getting (x, y) coordinates.
        move_coords = database[map_index][map_coords][move_choice]

        return move_coords, move_choice

    @staticmethod
    def __check_if_map_in_database(map, database):
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

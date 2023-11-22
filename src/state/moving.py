from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import random
import time

import cv2 as cv
import pyautogui as pyag

from .botstate_enum import BotState
import detection as dtc
from pop_up import PopUp
import window_capture as wc


class Moving:

    map_coords = None
    data_map = None

    __state = None
    __emergency_teleports = 0

    def __init__(self, controller):
        self.__controller = controller

    def moving(self):
        """'MOVING' state logic."""
        attempts_total = 0
        attempts_allowed = 3

        while attempts_total < attempts_allowed:

            if self.map_coords == "1,-25":

                if self.__detect_lumberjack_ws_interior():
                    log.info("Trying to exit the workshop ... ")
                    pyag.keyDown('e')
                    pyag.moveTo(667, 507)
                    pyag.click()
                    pyag.keyUp('e')
                    
                    if self.__detect_if_map_changed():
                        log.info("Successfuly exited the workshop!")
                        self.__state = BotState.CONTROLLER
                        return self.__state
                    else:
                        log.error(f"Failed to exit the workshop!")
                        attempts_total += 1
                        continue

            if self.__change_map(self.data_map, self.map_coords):
                # Resetting emergency teleport count to 0 after a
                # successful map change. Means character is not stuck
                # and good to go.
                self.__emergency_teleports = 0
                self.__controller.set_was_map_searched(False)
                self.__controller.set_was_map_changed(True)
                self.__state = BotState.CONTROLLER
                return self.__state
            else:
                PopUp.deal()
                attempts_total += 1     
                self.map_coords = self.get_coordinates(self.data_map)
                continue

        else:
            log.error(f"Failed to change maps in {attempts_allowed} "
                      "attempts!")
            if self.emergency_teleport():
                self.__state = BotState.CONTROLLER
                return self.__state

    def get_coordinates(self, database):
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
        # Taking screenshot of coordinate are to help determine if 
        # map tooltip appears later in the script.
        coord_area = self.__screenshot_coordinate_area()
        # Stores if coordinate detection failed first time. Sometimes
        # happens when Dofus is laggy. Especially in crowded areas.
        detection_failed = False
        # Loop control variables.
        start_time = time.time()
        timeout = 20

        while time.time() - start_time < timeout:

            log.info(f"Getting map coordinates ... ")

            # Moving mouse over the red area on the minimap for the 
            # black map tooltip to appear.
            pyag.moveTo(517, 680)

            # If detection failed first time, then sleep for a second
            # to allow time for map tooltip to appear. Usually first
            # time detection fails when Dofus is laggy.
            if detection_failed:
                log.debug("Sleeping 1 second before detection to allow map " 
                          "tooltip to appear ... ")
                time.sleep(1)

            # If map tooltip didn't appear - restart loop.
            if not self.__detect_map_tooltip(coord_area):
                if PopUp.detect_offers():
                    PopUp.deal()
                continue
            else:
                log.debug(f"Map tooltip detected!")
                
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
                log.error(f"Coordinate detection failed!")
                # Dealing with any offers/interfaces before retrying.
                PopUp.deal()
                detection_failed = True
                continue

            if self.__check_if_map_in_database(coords, database):
                log.info(f"Character is currently on map ({coords})!")
                return coords
            else:
                log.error(f"Map ({coords}) doesn't exist in database!")
                self.emergency_teleport()

        else:
            log.error("Error in 'get_coordinates()'!")
            log.error(f"Exceeded detection limit of {timeout} second(s)!")
            self.emergency_teleport()

    def get_map_type(self, database, map_coordinates):
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

    def emergency_teleport(self):
        """Teleport using 'Recall Potion' when stuck somewhere."""
        PopUp.deal()

        if self.__emergency_teleports >= 3:
            log.critical(f"Emergency teleport limit exceeded!")
            log.critical(f"Exiting ... ")
            wc.WindowCapture.on_exit_capture()

        elif self.__controller.banking.recall_potion_available():

            self.__emergency_teleports += 1
            log.info(f"Emergency teleports: {self.__emergency_teleports}")

            if self.__controller.banking.recall():
                log.info("Emergency teleport successful!")
                return True
            else:
                log.error(f"Emergency teleport failed!")

        else:
            wc.WindowCapture.on_exit_capture()

    def loading_screen(self, wait_time):
        """Detect beginning and end of 'Loading Map' screen."""
        start_time = time.time()

        while time.time() - start_time < wait_time:

            if self.__detect_black_pixels():
                log.debug("'Loading Map' screen detected!'")

                while time.time() - start_time < wait_time:

                    if not self.__detect_black_pixels():
                        log.debug("Finished loading!")
                        return True
                    else:
                        continue

                else:
                    log.error("Failed to detect end of 'Loading Map' screen "
                              f"in {wait_time} second(s)!")
                    return False

            else:
                continue

        else:
            log.error(f"Failed to detect 'Loading Map' screen in {wait_time} "
                      "second(s)!")
            return False

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
        screenshot = wc.WindowCapture.custom_area_capture(
                capture_region=(525, 650, 45, 30),
                conversion_code=cv.COLOR_RGB2GRAY,
                interpolation_flag=cv.INTER_LINEAR,
                scale_width=100,
                scale_height=100
            )
        return screenshot

    def __detect_if_map_changed(self):
        """Check if map was changed successfully."""
        # How long to keep checking if map was changed.
        wait_map_change = 10
        if self.loading_screen(wait_map_change):
            log.info(f"Map changed successfully!")
            return True
        else:
            log.error(f"Failed to change maps!")
            return False

    def __change_map(self, database, map_coords):
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
        # Time to wait before clicking on yellow 'sun' to change maps.
        # Must wait when moving in 'bottom' direction, because 'Dofus' 
        # GUI blocks the sun otherwise.
        wait_bottom_click = 0.5

        # Changing maps.
        PopUp.close_right_click_menu()
        coords, choice = self.__get_move_coords(database, map_coords)
        log.info(f"Clicking on: {coords[0], coords[1]} to move {choice} ... ")
        pyag.keyDown('e')
        pyag.moveTo(coords[0], coords[1])
        if choice == "bottom":
            time.sleep(wait_bottom_click)
        pyag.click()
        pyag.keyUp('e')

        # Checking if map was changed.
        if self.__detect_if_map_changed():
            return True
        else:
            return False

    def __detect_map_tooltip(self, screenshot_before):
        """
        Detect map tooltip on minimap.
        
        Parameters
        ----------
        screenshot_before : np.ndarray
            Image to compare against. Prefferably taken with
            '__screenshot_coordinate_area()'.

        Returns
        ----------
        True : bool
            If map tooltip detected.
        False : bool
            If failed to detect map tooltip.
        
        """
        start_time = time.time()
        timeout = 3

        while time.time() - start_time < timeout:

            screenshot_after = self.__screenshot_coordinate_area()

            rects = dtc.Detection.find(
                    screenshot_before, 
                    screenshot_after,
                    threshold = 0.99
                )

            if len(rects) <= 0:
                return True

        else:
            return False

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

    @staticmethod
    def __detect_black_pixels():
        """Detect black pixels on specified coordinates."""
        color = [0, 0, 0]
        coords = [(529, 491), (531, 429), (364, 419), (691, 424)]
        pixels = []

        for coord in coords:
            px = pyag.pixelMatchesColor(coord[0], coord[1], color)
            pixels.append(px)

        if all(pixels):
            return True
        else:
            return False

    @staticmethod
    def __screenshot_coordinate_area():
        """
        Screenshot area where map tooltip has to appear when mouse
        is hovered over red area on minimap.

        """
        screenshot = wc.WindowCapture.custom_area_capture(
                capture_region=(525, 650, 20, 30),
                conversion_code=cv.COLOR_RGB2GRAY,
                interpolation_flag=cv.INTER_LINEAR,
                scale_width=160,
                scale_height=200
            )
        return screenshot

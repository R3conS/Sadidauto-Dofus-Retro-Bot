"""Provides combat functionality."""

from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True)

import os
import time

import cv2 as cv
import pyautogui

from detection import Detection
from data import CombatData
from window_capture import WindowCapture


class Combat:
    """
    Holds methods related to combat.

    Instance attributes
    ----------
    character_name : str
        Character's nickname.

    Public class attributes
    ----------
    data_spell_cast : list[dict]
        Stores spell cast data based on loaded bot script (in 'bot.py').
    data_movement : list[dict]
        Stores movement data based on loaded bot script (in 'bot.py').

    Methods
    ----------
    get_ap()
        Get current 'AP' of character.
    get_mp()
        Get current 'MP' of character.
    turn_detect_start()
        Detect if turn started.
    turn_detect_end()
        Detect if turn ended.
    turn_pass()
        Pass turn.
    get_available_spells()
        Get all castable spells.
    get_spell_status()
        Check if spell is available to cast.
    get_spell_coordinates()
        Get coordinates of spell in spellbar.
    get_spell_cast_coordinates()
        Get coordinates of point to click on to cast spell.
    get_movement_coordinates()
        Get coordinates to click on to move character on correct cell.
    get_if_char_on_correct_cell()
        Check if character is standing on correct cell.
    get_char_position()
        Get (x, y) position of character on screen.
    move_character()
        Click on provided coordinates to move character.
    cast_spell()
        Cast spell.
    hide_models()
        Hide player and monster models.

    """

    # Constants.
    # Giving time for spell animation to finish.
    __WAIT_BETWEEN_SPELL_CASTS = 0.5
    # Giving time for "Illustration to signal your turn" to disappear.
    # Otherwise when character passes quickly at the start of turn,
    # detection starts too early and falsely detects another turn.
    __WAIT_AFTER_TURN_PASS = 0.5

    # Private class attributes.
    # 'Pyautogui' mouse movement duration. Default is 0.1, basically
    # instant. Messes up spell casting if left on default.
    __move_duration = 0.15

    # Objects.
    __window_capture = WindowCapture()
    __detection = Detection()

    # Public class attributes.
    # Stores spell cast data based on loaded bot script (in 'bot.py').
    data_spell_cast = None
    # Stores movement data based on loaded bot script (in 'bot.py').
    data_movement = None

    def __init__(self, character_name: str):
        """
        Constructor

        Parameters
        ----------
        character_name : str
            Character's nickname.

        """
        self.character_name = character_name

    def get_ap(self):
        """
        Get current 'AP' of character.

        Returns
        ----------
        r_and_t[0][1] : int
            Current number of 'AP' as `int`.
        None : NoneType
            If 'AP' count couldn't be detected.

        """
        ap_screenshot = self.__window_capture.custom_area_capture(
                self.__window_capture.AP_DETECTION_REGION,
                cv.COLOR_RGB2GRAY,
                cv.INTER_LINEAR,
                scale_width=215,
                scale_height=200
            )

        r_and_t, _, _ = self.__detection.detect_text_from_image(ap_screenshot)

        # If the count is not detected, most likely:
        # 1) mouse cursor or something else is blocking the area where 
        # 'custom_area_capture()' takes a screenshot.
        # 2) the 'capture_region' argument in 'custom_area_capture()' 
        # is wrong.
        if len(r_and_t) <= 0:
            log.info("Couldn't detect current 'AP' count!")
            return None

        return r_and_t[0][1]

    def get_mp(self):
        """
        Get current 'MP' of character.

        Returns
        ----------
        r_and_t[0][1] : int
            Current number of 'MP' as `int`.
        None : NoneType
            If 'MP' count couldn't be detected.

        """
        mp_screenshot = self.__window_capture.custom_area_capture(
                self.__window_capture.MP_DETECTION_REGION,
                cv.COLOR_RGB2GRAY,
                cv.INTER_LINEAR,
                scale_width=215,
                scale_height=200
            )

        r_and_t, _, _ = self.__detection.detect_text_from_image(mp_screenshot)

        # If the count is not detected, most likely:
        # 1) mouse cursor or something else is blocking the area where 
        # 'custom_area_capture()' takes a screenshot.
        # 2) the 'capture_region' argument in 'custom_area_capture()' 
        # is wrong.
        if len(r_and_t) <= 0:
            log.info("Couldn't detect current 'MP' count!")
            return None

        return r_and_t[0][1]

    def turn_detect_start(self):
        """
        Detect if turn started.
        
        Returns
        ----------
        True : bool
            If turn started.
        False : bool
            If turn has not started.

        """
        while True:
       
            px_1 = pyautogui.pixelMatchesColor(406, 106, (251, 103, 0),
                                               tolerance=5)
            px_2 = pyautogui.pixelMatchesColor(353, 109, (213, 208, 169),
                                               tolerance=3)
            px_3 = pyautogui.pixelMatchesColor(110, 100, (232, 228, 198),
                                               tolerance=3)

            if px_1 and px_2 and not px_3:

                screenshot = self.__window_capture.custom_area_capture(
                        self.__window_capture.TURN_START_REGION
                    )

                r_and_t, _, _ = self.__detection.detect_text_from_image(
                        screenshot
                    )

                if r_and_t:
                    if r_and_t[0][1] == self.character_name:
                        log.info("Turn started!")
                        return True
            else:
                return False

    def turn_detect_end(self):
        """
        Detect if turn ended.
        
        Returns
        ----------
        True : bool
            If turn has ended.
        False : bool
            If end of turn could not be detected within 'timeout_time'
            seconds.
        
        """
        start_time = time.time()
        timeout_time = 2
        while True:

            orange_pixel = pyautogui.pixelMatchesColor(
                    x=549,
                    y=630,
                    expectedRGBColor=(255, 102, 0),
                    tolerance=10
                )

            if time.time() - start_time > timeout_time:
                return False
            if not orange_pixel:
                return True

    def turn_pass(self):
        """
        Pass turn.
        
        Returns
        ----------
        True : bool
            If turn passed successfully.
        NoReturn
            Exits program if character couldn't pass turn within
            'timeout_time' seconds.

        """
        start_time = time.time()
        timeout_time = 30
        
        while time.time() - start_time < timeout_time:

            screenshot = self.__window_capture.custom_area_capture(
                    self.__window_capture.TURN_END_REGION
                )

            rects = self.__detection.find(
                    screenshot, 
                    CombatData.icon_turn_pass
                )

            if len(rects) > 0:
                log.info("Passing turn ... ")
                coords = self.__detection.get_click_coords(
                        rects,
                        self.__window_capture.TURN_END_REGION
                    )
                pyautogui.moveTo(coords[0][0],
                                 coords[0][1],
                                 duration=self.__move_duration)
                pyautogui.click()
                # Moving mouse off 'pass turn' button.
                pyautogui.move(0, 30)
                time.sleep(self.__WAIT_AFTER_TURN_PASS)
                
                if self.turn_detect_end():
                    log.info("Turn passed successfully!")
                    return True
                else:
                    log.error("Failed to pass turn!")
        else:
            log.critical(f"Couldn't pass turn for {timeout_time} second(s)!")
            log.critical("Timed out!")
            log.critical("Exiting ... ")
            WindowCapture.on_exit_capture()

    def get_available_spells(self):
        """
        Get all castable spells.

        Returns
        ----------
        available_spells : list[str]
            `list` of available spells as `str`.

        """
        available_spells = []
        for spell in CombatData.Spell.spells:
            if self.get_spell_status(spell):
                available_spells.append(spell)
        return available_spells

    def get_spell_status(self, spell, threshold=0.85):
        """
        Check if spell is available to cast.
        
        Parameters
        ----------
        spell : str
            Name of `spell`.
        threshold : float, optional
            Detection `threshold` used in `find()`. Defaults to 0.85.

        Returns
        ----------
        True : bool
            If `spell` is available.
        False : bool
            If `spell` is not available.
        
        """
        screenshot = self.__window_capture.custom_area_capture(
                    self.__window_capture.SPELL_BAR_REGION
                )

        rects = self.__detection.find(screenshot, spell, threshold=threshold)

        if len(rects) > 0:
            return True
        else:
            return False

    def get_spell_coordinates(self, spell, threshold=0.85):
        """
        Get coordinates of spell in spellbar.

        Parameters
        ----------
        spell : str
            Name of `spell`.
        threshold : float, optional
            Detection `threshold` used in `find()`. Defaults to 0.85.

        Returns
        ----------
        coords[0][0], coords[0][1] : Tuple[int, int]
            (x, y) coordinates of `spell` in spellbar.
        False : bool
            If coordinates couldn't be detected.
        
        """
        screenshot = self.__window_capture.custom_area_capture(
                    self.__window_capture.SPELL_BAR_REGION
                )

        rects = self.__detection.find(screenshot, spell, threshold=threshold)

        if len(rects) > 0:
            coords = self.__detection.get_click_coords(
                    rects,
                    self.__window_capture.SPELL_BAR_REGION
                )
            return coords[0][0], coords[0][1]
        return False

    def get_spell_cast_coordinates(self, 
                                   spell, 
                                   map_coordinates,
                                   start_cell_color,
                                   start_cell_coordinates):
        """
        Get coordinates of point to click on to cast spell.
        
        Parameters
        ----------
        spell : str
            Name of `spell`.
        map_coordinates : str
            Current map's coordinates.
        start_cell_color : str
            Color of starting cell.
        start_cell_coordinates : Tuple[int, int]
            Coordinates of starting cell.

        Returns
        ----------
        coordinates : Tuple[int, int]
            (x, y) `coordinates` of where to click to cast `spell`.

        """
        # Getting spell name out of path to spell image.
        if "." in spell:
            spell = spell.split(".")
            spell = spell[0]
            if "\\" in spell:
                spell = spell[::-1]
                spell = spell.split("\\")
                spell = spell[0][::-1]

        # Converting parameters to be compatible with keys in 'data.py'.
        if spell == "earthquake":
            spell = "e"
        elif spell == "poisoned_wind":
            spell = "p"
        elif spell == "sylvan_power":
            spell = "s"

        if start_cell_color == "red":
            start_cell_color = "r"
        elif start_cell_color == "blue":
            start_cell_color = "b"

        # Getting cast coordinates.
        coords = None
        for _, value in enumerate(self.data_spell_cast):
            for i_key, i_value in value.items():
                if i_key == map_coordinates:
                    for j_key, j_value in i_value.items():
                        if j_key == start_cell_color:
                            if isinstance(j_value[spell], dict):
                                coords = j_value[spell][start_cell_coordinates]
                                return coords
                            else:
                                coords = j_value[spell]
                                return coords

    def get_movement_coordinates(self, 
                                 map_coordinates, 
                                 start_cell_color,
                                 start_cell_coordinates):
        """
        Get coordinates to click on to move character on correct cell.

        Parameters
        ----------
        map_coordinates : str
            Current map's coordinates.
        start_cell_color : str
            Starting cell's color.
        start_cell_coordinates : Tuple[int, int]
            Starting cell's (x, y) coordinates.

        Returns
        ----------
        cell_coords : tuple[int, int]
            (x, y) coordinates of cell to click on.

        """
        for _, value in enumerate(self.data_movement):
            for i_key, i_value in value.items():
                if i_key == map_coordinates:
                    for j_key, j_value in i_value.items():
                        if j_key == start_cell_color:
                            if isinstance(j_value, dict):
                                cell_coords = j_value[start_cell_coordinates]
                                return cell_coords
                            else:
                                cell_coords = j_value
                                return cell_coords

    def get_if_char_on_correct_cell(self, cell_coordinates):
        """
        Check if character is standing on correct cell.

        Parameters
        ----------
        cell_coordinates : tuple[int, int]
            (x, y) coordinates of cell to check.
        
        Returns
        ----------
        True : bool
            If character is standing on correct cell.
        False : bool
            If character is standing on wrong cell.

        """
        x, y = cell_coordinates

        # All colors except last one are from tactical mode.
        # First one is from 'Ascalion', next 4 are from official 
        # 'Dofus Retro'. The last color is orange color that appears when 
        # cursor is hovered over cells for movement.
        colors = [(142, 134, 94), (152, 170, 94), (161, 180, 100),
                  (118, 122, 127), (131, 135, 141), (255, 102, 0)]

        # Comparing every color from 'colors' list to pixel color 
        # at (x, y) coordinates. Counting failed matches.
        counter = 0
        for color in colors:
            pixel = pyautogui.pixelMatchesColor(x, y, color)
            if not pixel:
                counter += 1

        # If no colors from 'colors' list match pixel color at
        # (x, y), then character is standing on correct cell.
        if counter == len(colors):
            return True
        else:
            return False

    def get_char_position(self, start_cell_color="red"):
        """
        Get (x, y) position of character on screen.

        Note
        ----------
        `start_cell_color` should always be 'red', unless developing or
        testing on PvP combat. Only during PvP `start_cell_color` can
        be 'blue'. During normal PvM it's always 'red'.

        Parameters
        ----------
        start_cell_color : str, optional 
            Color of starting cell. Defaults to "red".

        Returns
        ----------
        position : Tuple[int, int]
            (x, y) position of character.
        False : bool
            If position of character couldn't be detected.

        """
        coords = self.__get_pixel_coords(start_cell_color)
        if coords is not None:
            position = self.__get_click_coords(coords[0], coords[1])
            return position
        else:
            log.info("Couldn't get character position!")
            return False

    def __get_pixel_coords(self, start_cell_color):
        """
        Get coordinates of first found 'red' or 'blue' pixel.

        - Takes a screenshot of game window (capture_region = `reg`).
        - Tries to find `start_cell_color`.
        - If found, returns (x, y) coordinates and `reg`.
        - If not found returns `None`.

        Parameters
        ----------
        start_cell_color : str  
            Color of starting cell.

        Returns
        ----------
        coords, reg : Tuple[Tuple[int, int], Tuple[int, int, int, int]]
            Coordinates of found pixel and capture region.
        None : NoneType
            If pixel wasn't found.

        """
        # Region of area to screenshot.
        reg = (0, 53, 933, 537)

        if start_cell_color == "red":
            start_cell_color = (255, 0, 0)
        elif start_cell_color == "blue":
            start_cell_color = (0, 0, 255)

        sc = self.__window_capture.gamewindow_capture(capture_region=reg,
                                                      convert=False)

        for x in range(sc.width):
            for y in range(sc.height):
                if sc.getpixel((x, y)) == start_cell_color:
                    coords = x, y
                    return coords, reg

        return None

    def __get_click_coords(self, pixel_coords, region):
        """
        Calculate clickable coordinates on screen.

        Parameters
        ----------
        pixel_coords : Tuple[int, int]
            (x, y) coordinates of pixel.
        region : Tuple[int, int, int, int]
            Region of screen where pixel was found.

        Returns
        ----------
        coords : Tuple[int, int]
            (x, y) coordinates to click on.

        """
        rects = [[pixel_coords[0], pixel_coords[1], 1, 1]]
        coords = self.__detection.get_click_coords(rects, region=region)
        coords = coords[0][0], coords[0][1]
        return coords

    def move_character(self, cell_coordinates):
        """
        Click on provided coordinates to move character.

        Parameters
        ----------
        cell_coordinates : tuple[int, int]
            Coordinates to click on.

        """
        x, y = cell_coordinates
        pyautogui.moveTo(x=x, y=y, duration=self.__move_duration)
        pyautogui.click()

    def cast_spell(self, spell, spell_coordinates, cast_coordinates):
        """
        Cast spell.
        
        Parameters
        ----------
        spell : str
            Name of `spell`.
        spell_coordinates : Tuple[int, int]
            (x, y) coordinates of `spell` in spellbar.
        cast_coordinates : Tuple[int, int]
            (x, y) coordinates of where to click to cast `spell`.
        
        """
        # Formatting spell name.
        if "." in spell:
            spell = spell.split(".")
            spell = spell[0]
            if "\\" in spell:
                spell = spell[::-1]
                spell = spell.split("\\")
                spell = spell[0][::-1]
                spell = spell.replace("_", " ")
                spell = spell.title()

        log.info(f"Casting spell: '{spell}' ... ")
        pyautogui.moveTo(spell_coordinates[0], 
                         spell_coordinates[1], 
                         duration=self.__move_duration)
        pyautogui.click()
        pyautogui.moveTo(cast_coordinates[0], 
                         cast_coordinates[1], 
                         duration=self.__move_duration)
        pyautogui.click()
        # Moving mouse off of character so that his information
        # doesn't block spell bar. If omitted, may mess up spell
        # detection in 'Bot.__fighting_cast_spells()'.
        pyautogui.moveTo(574, 749)
        time.sleep(self.__WAIT_BETWEEN_SPELL_CASTS)

    def hide_models(self):
        """
        Hide player and monster models.
        
        Returns
        ----------  
        True : bool
            If models were hidden successfully.
        False : bool
            If models were not hidden during `wait_time` seconds.

        """
        log.info("Hiding models ... ")

        x, y = (865, 533)
        color = (0, 153, 0)
        start_time = time.time()
        wait_time = 5

        while time.time() - start_time < wait_time:

            button_clicked = pyautogui.pixelMatchesColor(x, y, color)

            if button_clicked:
                log.info("Models hidden successfully!")
                return True
            else:
                pyautogui.moveTo(x, y, duration=self.__move_duration)
                pyautogui.click()
                pyautogui.moveTo(574, 749)

        else:
            log.error(f"Failed to hide models in {wait_time} seconds!")
            return False

    def enable_tactical_mode(self):
        """
        Enable tactical mode.
        
        Returns
        ----------  
        True : bool
            If tactical mode enabled.
        False : bool
            If tactical mode not enabled.

        """
        x, y = (843, 523)
        color = (0, 153, 0)
        start_time = time.time()
        wait_time = 5

        while time.time() - start_time < wait_time:

            button_clicked = pyautogui.pixelMatchesColor(x, y, color)

            if button_clicked:
                log.info("'Tactical Mode' enabled!")
                return True
            else:
                log.info("Enabling 'Tactical Mode' ... ")
                pyautogui.moveTo(x, y, duration=self.__move_duration)
                pyautogui.click()
                pyautogui.moveTo(574, 749)

        else:
            log.error(f"Failed to enable in {wait_time} seconds!")
            return False

    def shrink_turn_bar(self):
        """
        Shrink turn bar.
        
        - Click on white arrows to shrink the turn bar.
        - Check if the closest 'information card' has disappeared by 
        looping through all possible `colors` on its (x, y) location.
        - If any of the `colors` were found, the turn bar was shrunk
        successfully.

        Returns
        ----------  
        True : bool
            If turn bar was shrunk successfully.
        False : bool
            If turn bar was not shrunk.

        """
        log.info("Shrinking `Turn Bar` ... ")
        
        colors = [(255, 255, 255)]
        x, y = (925, 567)
        start_time = time.time()
        wait_time = 5

        while time.time() - start_time < wait_time:

            pyautogui.moveTo(x, y, self.__move_duration)
            pyautogui.click()

            for color in colors:
                pixel = pyautogui.pixelMatchesColor(869, 548, color)
                if not pixel:
                    log.info("Successfully shrunk 'Turn Bar'!")
                    return True

        else:
            log.error("Failed to shrink 'Turn Bar'!")
            return False

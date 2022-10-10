"""Provides combat functionality."""

import os
import time

import cv2 as cv
import pyautogui

from detection import Detection
from window_capture import WindowCapture


class CombatData:
    """Holds paths, verifiers."""

    images_path = "combat_images\\"
    icon_turn_pass = images_path + "icon_turn_pass.jpg"


class Spells:
    """Holds spell data."""

    e_quake = CombatData.images_path + "earthquake.jpg"
    p_wind = CombatData.images_path + "poisoned_wind.jpg"
    s_power = CombatData.images_path + "sylvan_power.jpg"
    spells = [e_quake, p_wind, s_power]

    # Spell cast data for 'Amakna Castle Gobballs'.
    acg = [
        {"3,-7": {"r": {"e": (  None  ), "p": (  None  ), "s": (  None  )}, 
                  "b": {"e": (  None  ), "p": (  None  ), "s": (  None  )}}},
        {"3,-8": {"r": {"e": (433, 238), "p": (  None  ), "s": (  None  )},
                  "b": {"e": (433, 238), "p": (  None  ), "s": (  None  )}}},
        {"3,-9": {"r": {"e": (467, 323), "p": (  None  ), "s": (  None  )},
                  "b": {"e": (467, 323), "p": (  None  ), "s": (  None  )}}},
        {"4,-8": {"r": {"e": (  None  ), "p": (  None  ), "s": (  None  )}, 
                  "b": {"e": (  None  ), "p": (  None  ), "s": (  None  )}}},
        {"4,-9": {"r": {"e": (  None  ), "p": (  None  ), "s": (  None  )}, 
                  "b": {"e": (  None  ), "p": (  None  ), "s": (  None  )}}},
        {"5,-8": {"r": {"e": (  None  ), "p": (  None  ), "s": (  None  )}, 
                  "b": {"e": (  None  ), "p": (  None  ), "s": (  None  )}}},
        {"5,-9": {"r": {"e": (465, 358), "p": (  None  ), "s": (  None  )}, 
                  "b": {"e": (465, 358), "p": (  None  ), "s": (  None  )}}},
    ]

    af = []


class Combat:
    """
    Holds methods related to combat.

    Instance attributes
    ----------
    character_name : str
        Character's nickname.

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
    cast_spell()
        Cast spell.

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
    # Stores spell casting data according to loaded bot script.
    __spell_cast_data = None

    # Objects
    __window_capture = WindowCapture()
    __detection = Detection()

    def __init__(self, character_name: str, script: str):
        """
        Constructor

        Parameters
        ----------
        character_name : str
            Character's nickname.

        """
        self.character_name = character_name

        # Loading proper spell cast data according to 'script'.
        # The validity of 'script' is checked within main bot logic.
        if isinstance(script, str):
            script = script.lower()
            if script == "amakna_castle_gobballs":
                self.__spell_cast_data = Spells.acg
            elif script == "astrub_forest":
                self.__spell_cast_data = Spells.af

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
            print("[INFO] Couldn't detect current 'AP' count!")
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
            print("[INFO] Couldn't detect current 'MP' count!")
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
       
            orange_px = pyautogui.pixelMatchesColor(407, 106, (250, 103, 0),
                                                    tolerance=3)
            white_px = pyautogui.pixelMatchesColor(407, 116, (247, 250, 244),
                                                   tolerance=3)
            gray_px = pyautogui.pixelMatchesColor(110, 100, (232, 228, 198),
                                                  tolerance=3)

            if orange_px and white_px and not gray_px:

                screenshot = self.__window_capture.custom_area_capture(
                        self.__window_capture.TURN_START_REGION
                    )

                r_and_t, _, _ = self.__detection.detect_text_from_image(screenshot)

                if r_and_t:
                    if r_and_t[0][1] == self.character_name:
                        print("[INFO] Turn started!")
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
        timeout_time = 10
        while time.time() - start_time < timeout_time:

            screenshot = self.__window_capture.custom_area_capture(
                    self.__window_capture.TURN_END_REGION
                )

            rects = self.__detection.find(
                    screenshot, 
                    CombatData.icon_turn_pass
                )

            if len(rects) > 0:
                print("[INFO] Passing turn ... ")
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
                    print("[INFO] Turn passed successfully!")
                    return True
                else:
                    print("[INFO] Failed to pass turn!")
        else:
            print(f"[ERROR] Couldn't pass turn for {timeout_time} second(s)!")
            print(f"[ERROR] Timed out!")
            print(f"[ERROR] Exiting ... ")
            os._exit(1)

    def get_available_spells(self):
        """
        Get all castable spells.

        Returns
        ----------
        available_spells : list[str]
            `list` of available spells as `str`.

        """
        available_spells = []
        for spell in Spells.spells:
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
                                   start_cell_coords,
                                   start_cell_color):
        """
        Get coordinates of point to click on to cast spell.
        
        Parameters
        ----------
        spell : str
            Name of `spell`.
        map_coordinates : str
            Current map's coordinates.
        start_cell_coords : Tuple[int, int]
            Coordinates of cell on which character started combat.
        start_cell_color : str
            Color of starting cell.

        Returns
        ----------
        coordinates : Tuple[int, int]
            (x, y) `coordinates` of where to click to cast `spell`.

        """
        # Converting parameters to be compatible with keys in
        # 'self.__spell_cast_data'.
        if "\\" in spell:
            spell = spell.split("\\")
            spell = spell[1].split(".")
            spell = spell[0]

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
        coordinates = None
        for _, value in enumerate(self.__spell_cast_data):
            for i_key, i_value in value.items():
                if i_key == map_coordinates:
                    for j_key, j_value in i_value.items():
                        if j_key == start_cell_color:
                            if j_value[spell] is not None:
                                coordinates = j_value[spell]
                                return coordinates
                            else:
                                coordinates = start_cell_coords
                                return coordinates

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
        spell = spell.split("\\")
        spell = spell[1].split(".")
        spell = spell[0].replace("_", " ")
        spell = spell.title()

        print(f"[INFO] Casting spell: {spell} ... ")
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
        # detection in 'Bot.__in_combat_cast_spells()'.
        pyautogui.moveTo(574, 749)
        time.sleep(self.__WAIT_BETWEEN_SPELL_CASTS)

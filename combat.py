"""Provides combat functionality."""

import time
from typing import Tuple

import cv2 as cv
import pyautogui

from detection import Detection
from window_capture import WindowCapture


class CombatData:


    images_path = "combat_images\\"
    earthquake = images_path + "earthquake.jpg"
    poisoned_wind = images_path + "poisoned_wind.jpg"
    sylvan_power = images_path + "sylvan_power.jpg"
    icon_pass_turn = images_path + "icon_pass_turn.jpg"
    end_turn_verifier = images_path + "end_turn_verifier.jpg"


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
    detect_turn_start()
        Detect if turn started.
    detect_turn_end()
        Detect if turn ended.
    pass_turn()
        Pass turn.
    check_spell_availability()
        Check if spell is available to cast.
    
    """

    # Objects
    __window_capture = WindowCapture()
    __detection = Detection()

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

    def detect_turn_start(self):
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

    def detect_turn_end(self):
        """
        Detect if turn ended.
        
        Returns
        ----------
        True : bool
            If turn has ended.
        False : bool
            If end of turn could not be detected.
        
        """
        start_time = time.time()
        exit_time = 10
        while True:

            screenshot = self.__window_capture.custom_area_capture(
                    self.__window_capture.TURN_END_REGION
                )

            rects = self.__detection.find(
                    screenshot,
                    CombatData.end_turn_verifier,
                )

            if time.time() - start_time > exit_time:
                print("[ERROR] Couldn't detect end of turn!")
                return False
            if len(rects) > 0:
                print("[INFO] Turn ended!")
                return True

    def pass_turn(self):
        """
        Pass turn.
        
        Returns
        ----------
        True : bool
            If turn passed successfully.
        False : bool
            If turn was not passed.

        """
        while True:

            screenshot = self.__window_capture.custom_area_capture(
                    self.__window_capture.TURN_END_REGION
                )

            rects = self.__detection.find(
                    screenshot, 
                    CombatData.icon_pass_turn
                )

            if len(rects) > 0:
                print("[INFO] Passing turn ... ")
                coords = self.__detection.get_click_coords(
                        rects,
                        self.__window_capture.TURN_END_REGION
                    )
                pyautogui.moveTo(coords[0][0], coords[0][1])
                pyautogui.click()

                if self.detect_turn_end():
                    print("[INFO] Turn passed successfully!")
                    return True
                else:
                    print("[ERROR] Failed to pass turn!")
                    return False

    def check_spell_availability(self, spell, threshold=0.85):
        """
        Check if spell is available to cast.
        
        Parameters
        ----------
        spell : str
            Name of spell.
        threshold : float, optional
            Detection threshold used in `find()`. Defaults to 0.85.

        Returns
        ----------
        coords[0][0], coords[0][1] : Tuple[int, int]
            (x, y) coordinates of `spell`.
        False : bool
            If spell is not available.
        
        """
        screenshot = self.__window_capture.custom_area_capture(
                    self.__window_capture.SPELL_BAR_REGION
                )

        rects = self.__detection.find(screenshot, spell, threshold=threshold)

        spell = spell.split("\\")
        spell = spell[1].split(".")
        spell = spell[0].replace("_", " ")
        spell = spell.title()

        if len(rects) > 0:
            print(f"[INFO] Spell '{spell}' is available!")
            coords = self.__detection.get_click_coords(
                    rects,
                    self.__window_capture.SPELL_BAR_REGION
                )
            return coords[0][0], coords[0][1]
        else:
            print(f"[INFO] Spell '{spell}' is NOT available!")
            return False

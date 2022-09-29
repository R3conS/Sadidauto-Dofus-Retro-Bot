"""Provides combat functionality."""

from typing import Tuple

import cv2 as cv

from detection import Detection
from window_capture import WindowCapture


class Combat:
    """
    Holds methods related to combat.

    Methods
    ----------
    get_ap()
        Get current 'AP' of character.
    get_mp()
        Get current 'MP' of character.

    """

    def __init__(self):
        """
        Constructor.

        Attributes
        ----------
        __window_capture : type[WindowCapture]
            Instance of 'WindowCapture' class.
        __detection : type[Detection]
            Instance of 'Detection' class.

        """
        self.__window_capture = WindowCapture()
        self.__detection = Detection()

    def get_ap(self) -> list[Tuple[list[int], str]] | None:
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
            cv.INTER_AREA,
            scale_width=215,
            scale_height=200)

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

    def get_mp(self) -> list[Tuple[list[int], str]] | None:
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
            cv.INTER_AREA,
            scale_width=215,
            scale_height=200)

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

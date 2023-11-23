"""Provides screen capturing functionality."""

from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import datetime
import os
from typing import Tuple
from time import time, sleep

import cv2 as cv
import numpy as np
import pyautogui

import interfaces as itf


class WindowCapture:
    """
    Holds various screenshotting methods.
    
    Methods
    ----------
    area_around_mouse_capture()
        Screenshot area around mouse cursor.
    custom_area_capture()
        Screenshot specified area.
    gamewindow_capture()
        Screenshot whole game window, including Windows top bar.
    on_exit_capture()
        Take a screenshot, logout and exit program.

    """

    @staticmethod
    def area_around_mouse_capture(midpoint: int,
                                  pos: Tuple[int, int] = pyautogui.position(),
                                  convert: bool = True):
        """
        Screenshot area around mouse cursor.

        Parameters
        ----------
        midpoint : int
            Midpoint of length and width value of screenshot area.
            Screenshot area in pixels: (`midpoint`*2) * (`midpoint*2`).
        pos : Tuple[int, int], optional
            Center (x, y) coordinates of screenshot area. Defaults to
            current coordinates of mouse cursor.
        convert : bool, optional
            Whether to convert image to `np.ndarray` or not. Defaults to 
            `True`.

        Returns
        ----------
        screenshot : np.ndarray
            If `convert` is `True`, return `screenshot` of area around 
            `pos`.
        screenshot, region : Tuple[PIL.Image, Tuple[int, int, int, int]]
            If `convert` is `False`, return `screenshot` as `PIL.Image` 
            object and `region` where the `screenshot` was taken on 
            screen as `tuple`.

        Raises
        ----------
        ValueError
            If `midpoint` < 0.
        (-215:Assertion failed)
            If `midpoint` == 0.

        """
        # Getting current (x, y) coordinates of mouse cursor.
        mouse_pos = pos
        center_x = mouse_pos[0]
        center_y = mouse_pos[1]
        # Calculating top left coordinates of capture area.
        topleft_x = center_x - midpoint
        topleft_y = center_y - midpoint
        # Calculating bottom right coordinates of capture area.
        bottomright_x = center_x + midpoint
        bottomright_y = center_y + midpoint
        # Calculating width and height of capture area.
        width = bottomright_x - topleft_x
        height = bottomright_y - topleft_y
        # Declaring the screenshot region.
        region = (int(topleft_x), int(topleft_y), int(width), int(height))
        # Taking the screenshot.
        screenshot = pyautogui.screenshot(region=region)
        if not convert:
            return screenshot, region
        else:
            screenshot = np.array(screenshot)
            screenshot = cv.cvtColor(screenshot, cv.COLOR_RGB2BGR)
            return screenshot

    @staticmethod
    def custom_area_capture(capture_region: Tuple[int, int, int, int],
                            conversion_code: int = cv.COLOR_RGB2BGR,
                            interpolation_flag: int = cv.INTER_LINEAR,
                            scale_width: int = 100,
                            scale_height: int = 100) \
                            -> np.ndarray:
        """
        Screenshot specified area.

        Screenshot can be upscaled/downscaled and/or converted to 
        different color space in place.
        
        Parameters
        ----------
        capture_region : tuple
            Region of the screen to screenshot in
            (topLeft_x, topLeft_y, width, height) format.
        conversion_code : int, optional
            OpenCV's color space conversion code. Defaults to:
            `cv.COLOR_RGB2BGR`.
        interpolation_flag : int, optional
            OpenCV's geometric image transformation interpolation flag.
            To shrink an image, it will generally look best with 
            `cv.INTER_AREA` interpolation, whereas to enlarge an image, 
            it will generally look best with `cv.INTER_CUBIC` (slow) 
            or `cv.INTER_LINEAR` (faster but still looks OK). Defaults 
            to `cv.INTER_LINEAR`.
        scale_width : int, optional
            Controls screenshot's width upscale/downscale percentage.
            100 is untouched. Defaults to: 100.
        scale_height : int, optional
            Controls screenshot's height upscale/downscale percentage.
            100 is untouched. Defaults to: 100.

        Returns
        ----------
        screenshot : np.ndarray
            Screenshot of specified area.

        """
        # Getting a screenshot.
        screenshot = pyautogui.screenshot(region=capture_region)
        screenshot = np.array(screenshot)
        screenshot = cv.cvtColor(screenshot, conversion_code)

        # Upscaling/downscaling the screenshot.
        width_percentage = scale_width
        height_percentage = scale_height
        width = int(screenshot.shape[1] * width_percentage / 100)
        height = int(screenshot.shape[0] * height_percentage / 100)
        dimensions = (width, height)
        screenshot = cv.resize(screenshot, 
                               dimensions, 
                               interpolation=interpolation_flag)

        return screenshot

    @staticmethod
    def gamewindow_capture(
            capture_region: Tuple[int, int, int, int] = (0, 0, 933, 755),
            conversion_code: int = cv.COLOR_RGB2BGR,
            convert: bool = True
        ):
        """
        Screenshot whole game window, including Windows top bar.

        Parameters
        ----------
        capture_region : tuple, optional
            Region of the screen to screenshot in
            (topLeft_x, topLeft_y, width, height) format. Defaults to:
            (0, 0, 933, 755).
        conversion_code: int, optional
            OpenCV color conversion code. Defaults to: 
            `cv.COLOR_RGB2BGR`.
        convert : bool, optional
            Whether to convert image to `np.ndarray` or not. Defaults to 
            `True`.

        Returns
        ----------
        screenshot : np.ndarray
            If `convert` is `True`, return `screenshot` as `np.ndarray`.
        screenshot : PIL.Image
            If `convert` is `False`, return `screenshot` as `PIL.Image`.

        """
        screenshot = pyautogui.screenshot(region=capture_region)
        if not convert:
            return screenshot
        else:
            screenshot = np.array(screenshot)
            screenshot = cv.cvtColor(screenshot, conversion_code)
            return screenshot

    @staticmethod
    def on_exit_capture(exit_dofus=True):
        """
        Take a screenshot, logout and exit program.
        
        Method is used after a critical error was encountered and
        program can't continue to run.

        """
        images_folder_name = "on_exit_images"
        images_folder_path = os.path.join(Logger.LOGS_DIR_PATH, images_folder_name)
        if images_folder_name not in os.listdir(Logger.LOGS_DIR_PATH):
            os.mkdir(images_folder_path)

        image_name = datetime.datetime.now().strftime("[%Y-%m-%d] Captured - %Hh %Mm %Ss") + ".jpg"
        log.info("Taking a screenshot for debug ... ")
        pyautogui.screenshot(os.path.join(images_folder_path, image_name))
        log.info(f"Saved: '{os.path.join(images_folder_path, image_name)}'!")

        if exit_dofus:
            # WindowCapture.__logout()
            os._exit(1)

    @staticmethod
    def __logout():
        log.info("Logging out ... ")
        start_time = time()
        timeout = 15
        while time() - start_time < timeout:
            # Opening 'Main Menu'.
            pyautogui.press("esc")
            sleep(0.5)
            if itf.Interfaces.detect_interfaces() == "main_menu":
                pyautogui.moveTo(468, 318, duration=0.15)
                pyautogui.click()
                sleep(0.5)
                if itf.Interfaces.detect_interfaces() == "caution":
                    pyautogui.moveTo(381, 371, duration=0.15)
                    pyautogui.click()
                    sleep(2.5)
                    if itf.Interfaces.detect_interfaces() == "login_screen":
                        log.info("Logged out successfully!")
                        break
        else:
            log.error(f"Failed to log out! Closing 'Dofus.exe' ...")
            pyautogui.moveTo(910, 15, duration=0.15)
            pyautogui.click()

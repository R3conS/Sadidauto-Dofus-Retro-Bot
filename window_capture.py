"""Provides screen capturing functionality."""

import threading
from typing import Tuple

import cv2 as cv
import numpy as np
import pyautogui

from threading_tools import ThreadingTools


class WindowCapture:
    """
    Holds various screenshotting methods.
    
    Methods
    ----------
    area_around_mouse_capture()
        Screenshot area around mouse cursor.
    custom_area_capture()
        Screenshot specified area.
    WindowCapture_Thread_start()
        Start window capturing thread.
    WindowCapture_Thread_stop()
        Stop window capturing thread.

    """

    # Constants.
    # Region of whole game window. Includes windows top bar.
    __GAMEWINDOW_REGION = (0, 0, 933, 755)
    # Region to screenshot for map detection.
    MAP_DETECTION_REGION = (522, 650, 48, 30)
    # Region to screenshot for AP/MP detection.
    AP_DETECTION_REGION = (465, 610, 20, 25)
    MP_DETECTION_REGION = (570, 615, 15, 25)

    # Class attributes.
    screenshot_for_obj_detection = None
    screenshot_for_VDO_Thread = None

    # Threading attributes.
    __WindowCapture_Thread_stopped = True
    __WindowCapture_Thread_lock = threading.Lock()
    __WindowCapture_Thread_thread = None

    # Objects.
    __threading_tools = ThreadingTools()

    def __gamewindow_capture(
            self,
            capture_region: Tuple[int, int, int, int] = __GAMEWINDOW_REGION,
            conversion_code: int = cv.COLOR_RGB2BGR) \
            -> Tuple[np.ndarray, np.ndarray]:
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

        Returns
        ----------
        sc_obj_detection : np.ndarray
            Screenshot for object detection.
        sc_VDO_Thread : np.ndarray
            Screenshot for visual debug output.

        """
        sc_obj_detection = pyautogui.screenshot(region=capture_region)
        sc_obj_detection = np.array(sc_obj_detection)
        sc_obj_detection = cv.cvtColor(sc_obj_detection, conversion_code)

        sc_VDO_Thread = pyautogui.screenshot(region=capture_region)
        sc_VDO_Thread = np.array(sc_VDO_Thread)
        sc_VDO_Thread = cv.cvtColor(sc_VDO_Thread, conversion_code)

        return sc_obj_detection, sc_VDO_Thread

    def area_around_mouse_capture(self, midpoint: int) -> np.ndarray:
        """
        Screenshot area around mouse cursor.

        Parameters
        ----------
        midpoint : int
            Midpoint of length and width value of screenshot area.
            Screenshot area in pixels: (`midpoint`*2) * (`midpoint*2`).

        Returns
        ----------
        screenshot : np.ndarray
            Screenshot of area around the mouse cursor.

        Raises
        ----------
        ValueError
            If `midpoint` < 0.
        (-215:Assertion failed)
            If `midpoint` == 0.

        """
        # Getting current (x, y) coordinates of mouse cursor.
        mouse_pos = pyautogui.position()
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
        capture_region = (topleft_x, topleft_y, width, height)
        # Taking the screenshot.
        screenshot = pyautogui.screenshot(region=capture_region)
        screenshot = np.array(screenshot)
        screenshot = cv.cvtColor(screenshot, cv.COLOR_RGB2BGR)

        return screenshot

    def custom_area_capture(self, 
                            capture_region: Tuple[int, int, int, int],
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
            to: `cv.INTER_LINEAR`.
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

#----------------------------------------------------------------------#
#--------------------------THREADING METHODS---------------------------#
#----------------------------------------------------------------------#

    def WindowCapture_Thread_start(self):
        """Start window capturing thread."""
        self.__WindowCapture_Thread_stopped = False
        self.__WindowCapture_Thread_thread = threading.Thread(
                target=self.__WindowCapture_Thread_run
            )
        self.__WindowCapture_Thread_thread.start()
        self.__threading_tools.wait_thread_start(
                self.__WindowCapture_Thread_thread
            )

    def WindowCapture_Thread_stop(self):
        """Stop window capturing thread."""
        self.__WindowCapture_Thread_stopped = True
        self.__threading_tools.wait_thread_stop(
                self.__WindowCapture_Thread_thread
            )

    def __WindowCapture_Thread_run(self):
        """Execute this code while thread is alive."""
        while not self.__WindowCapture_Thread_stopped:
            # Getting an updated image (screenshot) of the game.
            sc_obj_detection, sc_VDO_Thread = self.__gamewindow_capture()
            # Locking the thread while updating the results.
            self.__WindowCapture_Thread_lock.acquire()
            self.screenshot_for_obj_detection = sc_obj_detection
            self.screenshot_for_VDO_Thread = sc_VDO_Thread
            self.__WindowCapture_Thread_lock.release()

#----------------------------------------------------------------------#

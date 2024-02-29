from src.logger import get_logger

log = get_logger()

from time import perf_counter

import numpy as np
from cv2 import TM_CCOEFF_NORMED
from pyautogui import click, moveTo

from src.bot._exceptions import RecoverableException
from src.utilities.general import move_mouse_off_game_area
from src.utilities.image_detection import ImageDetection
from src.utilities.screen_capture import ScreenCapture


class Interface:

    def __init__(self, name):
        self._name = name

    def open(self, x, y, is_open_func: callable, action_timeout=5):
        log.info(f"Opening '{self._name}' interface ... ")
        if is_open_func():
            log.info(f"'{self._name}' interface is already open!")
            return

        moveTo(x, y)
        click()

        start_time = perf_counter()
        while perf_counter() - start_time <= action_timeout:
            if is_open_func():
                log.info(f"Successfully opened '{self._name}' interface!")
                move_mouse_off_game_area()
                return

        raise RecoverableException(f"Failed to open '{self._name}' interface.")

    def close(self, x, y, is_open_func: callable, action_timeout=5):
        log.info(f"Closing '{self._name}' interface ... ")
        if not is_open_func():
            log.info(f"'{self._name}' interface is already closed!")
            return

        moveTo(x, y)
        click()

        start_time = perf_counter()
        while perf_counter() - start_time <= action_timeout:
            if not is_open_func():
                log.info(f"Successfully closed '{self._name}' interface!")
                move_mouse_off_game_area()
                return

        raise RecoverableException(f"Failed to close '{self._name}' interface.")

    def click_button(
            self, 
            button_name, 
            button_area, 
            button_images, 
            is_open_func: callable, 
            is_opening: bool, # Whether to check if the interface is open or closed after clicking.
            action_timeout=5
        ):
        log.info(f"Clicking '{button_name}' button ... ")
        moveTo(*self._get_button_pos(button_area, button_images))
        click()
        start_time = perf_counter()
        while perf_counter() - start_time <= action_timeout:
            if (
                (is_opening and is_open_func())
                or (not is_opening and not is_open_func())
            ):
                log.info(f"Successfully clicked '{button_name}' button!")
                move_mouse_off_game_area()
                return
        raise RecoverableException(
            f"Failed to detect if '{button_name}' button was clicked. "
            f"Timeout: {action_timeout} seconds."
        )

    @staticmethod
    def _get_button_pos(search_area, images: list[np.ndarray]):
        sc = ScreenCapture.custom_area(search_area)
        rectangles = ImageDetection.find_images(
            haystack=sc, 
            needles=images,
            confidence=0.9,
            method=TM_CCOEFF_NORMED
        )
        if len(rectangles) > 0:
            return ImageDetection.get_rectangle_center_point(
                (
                    rectangles[0][0] + search_area[0], 
                    rectangles[0][1] + search_area[1], 
                    rectangles[0][2], 
                    rectangles[0][3]
                )
            )
        raise RecoverableException("Failed to find button position.")

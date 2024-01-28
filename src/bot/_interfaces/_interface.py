from src.logger import Logger
log = Logger.get_logger(Logger.DEBUG, True, True)

from time import perf_counter

import numpy as np
from pyautogui import click, moveTo

from src.bot._exceptions import RecoverableException
from src.utilities.general import move_mouse_off_game_area
from src.utilities.image_detection import ImageDetection
from src.utilities.ocr.ocr import OCR
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
            search_area: tuple[int, int, int, int], # (x, y, width, height).
            button_text: str, 
            is_open_func: callable, 
            action_timeout=5
        ):
        image_scale = 3
        sc = self._prepare_image(search_area, image_scale)
        sc_copy = sc.copy()

        binarization_threshold = 70
        while binarization_threshold <= 115:
            sc = OCR.binarize_image(sc_copy, binarization_threshold)
            result = OCR.get_text_from_image(sc, with_rectangles=True)
            if self._is_button_text_found(button_text, result):
                x, y = self._get_button_text_center_point(button_text, result, search_area, image_scale)
                self._click_button_text_center_point(x, y, button_text, is_open_func, action_timeout)
                return
            else:
                binarization_threshold += 5
                continue

        raise RecoverableException(f"Failed to find the '{button_text}' button.")

    def _prepare_image(self, search_area: tuple[int, int, int, int], image_scale) -> np.ndarray:
        sc = ScreenCapture.custom_area(search_area)
        sc = OCR.resize_image(sc, sc.shape[1] * image_scale, sc.shape[0] * image_scale)
        sc = OCR.convert_to_grayscale(sc)
        return OCR.invert_image(sc)

    def _is_button_text_found(self, button_text: str, ocr_result) -> bool:
        return any(word == button_text for word, _ in ocr_result)

    def _get_button_text_center_point(
        self, 
        button_text: str, 
        ocr_result: tuple[str, tuple[int, int, int, int]], 
        search_area: tuple[int, int, int, int],
        image_scale: int
    ):
        for word, rectangle in ocr_result:
            if word == button_text:
                rectangle = tuple(int(x / image_scale) for x in rectangle)
                rectangle = (
                    rectangle[0] + search_area[0], 
                    rectangle[1] + search_area[1], 
                    rectangle[2], 
                    rectangle[3]
                )
                return ImageDetection.get_rectangle_center_point(rectangle)

    def _click_button_text_center_point(
        self, 
        x: int,
        y: int,
        button_text: str, 
        is_open_func: callable, 
        action_timeout: int
    ):
        log.info(f"Clicking the '{button_text}' button ... ")
        moveTo(x, y)
        click()
        start_time = perf_counter()
        while perf_counter() - start_time <= action_timeout:
            if not is_open_func():
                log.info(f"Successfully clicked the '{button_text}' button!")
                move_mouse_off_game_area()
                return
        raise RecoverableException(
            f"Timed out while detecting if '{button_text}' button was clicked successfully. "
            f"Timeout: {action_timeout} seconds."
        )

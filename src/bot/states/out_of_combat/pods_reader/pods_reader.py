from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from datetime import datetime
import os
from time import perf_counter
import re

from functools import wraps

import cv2
import numpy as np
import pyautogui as pyag

from src.ocr.ocr import OCR
from src.screen_capture import ScreenCapture


def _is_tooltip_visible(decorated_method):
    @wraps(decorated_method)
    def wrapper(cls, *args, **kwargs):
        tooltip_name = decorated_method.__name__.split("_")[1]
        screenshot_tooltip_area = getattr(cls, f"screenshot_{tooltip_name}_tooltip_area")
        get_tooltip_rectangle = getattr(cls, f"get_{tooltip_name}_tooltip_rectangle")
        if get_tooltip_rectangle(screenshot_tooltip_area()) is not None:
            return True
        return False
    return wrapper


def _get_pods_numbers(decorated_method):
    @wraps(decorated_method)
    def wrapper(cls, *args, **kwargs):
        tooltip_name = decorated_method.__name__.split("_")[1]
        trigger_tooltip = getattr(cls, f"trigger_{tooltip_name}_tooltip")
        is_tooltip_visible = getattr(cls, f"is_{tooltip_name}_tooltip_visible")
        screenshot_tooltip_area = getattr(cls, f"screenshot_{tooltip_name}_tooltip_area")
        get_tooltip_rectangle = getattr(cls, f"get_{tooltip_name}_tooltip_rectangle")
        hide_tooltip = getattr(cls, f"hide_{tooltip_name}_tooltip")

        trigger_tooltip()
        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if is_tooltip_visible():
                tooltip_area = screenshot_tooltip_area()
                tooltip_rectangle = get_tooltip_rectangle(tooltip_area)
                hide_tooltip()
                if tooltip_rectangle is not None:
                    tooltip = cls.crop_tooltip_from_image(tooltip_area, tooltip_rectangle)
                    text = cls.read_tooltip_text(tooltip)
                    return cls.parse_tooltip_text(text)
        log.error(f"Timed out while getting {tooltip_name} pods numbers.")
        cls.save_images_for_debug()
        return None
    return wrapper


def _get_occupied_pods(decorated_method):
    @wraps(decorated_method)
    def wrapper(cls, *args, **kwargs):
        tooltip_name = decorated_method.__name__.split("_")[2]
        numbers = getattr(cls, f"get_{tooltip_name}_numbers")()
        if numbers is not None:
            return numbers[0]
        return None
    return wrapper


def _get_total_pods(decorated_method):
    @wraps(decorated_method)
    def wrapper(cls, *args, **kwargs):
        tooltip_name = decorated_method.__name__.split("_")[2]
        numbers = getattr(cls, f"get_{tooltip_name}_numbers")()
        if numbers is not None:
            return numbers[1]
        return None
    return wrapper


def _get_percentage(decorated_method):
    @wraps(decorated_method)
    def wrapper(cls, *args, **kwargs):
        tooltip_name = decorated_method.__name__.split("_")[2]
        numbers = getattr(cls, f"get_{tooltip_name}_numbers")()
        if numbers is not None:
            return round(numbers[0] / numbers[1] * 100, 2)
        return None
    return wrapper


class PodsReader:
    """
    For getter methods to work the according interface has to be open.
    - `bank` refers to pods in inventory when bank vault is open.
    - `inventory` refers to pods when regular inventory interface is open.
    """

    @classmethod
    @_get_occupied_pods
    def get_occupied_bank_pods(cls) -> int:
        pass

    @classmethod
    @_get_occupied_pods
    def get_occupied_inventory_pods(cls) -> int:
        pass

    @classmethod
    @_get_total_pods
    def get_total_bank_pods(cls) -> int:
        pass

    @classmethod
    @_get_total_pods
    def get_total_inventory_pods(cls) -> int:
        pass

    @classmethod
    @_get_percentage
    def get_occupied_bank_percentage(cls) -> float:
        """Get occupied bank pods as a percentage."""
        pass

    @classmethod
    @_get_percentage
    def get_occupied_inventory_percentage(cls) -> float:
        """Get occupied inventory pods as a percentage."""
        pass

    @classmethod
    @_get_pods_numbers
    def get_bank_numbers(cls) -> tuple[int, int]:
        """Get the occupied and total pods while bank vault is open."""
        pass

    @classmethod
    @_get_pods_numbers
    def get_inventory_numbers(cls) -> tuple[int, int]:
        """Get the occupied and total pods while inventory interface is open."""
        pass

    @staticmethod
    def trigger_bank_tooltip():
        pyag.moveTo(735, 560)

    @staticmethod
    def hide_bank_tooltip():
        pyag.moveTo(735, 580)

    @staticmethod
    def trigger_inventory_tooltip():
        pyag.moveTo(594, 338)

    @staticmethod
    def hide_inventory_tooltip():
        pyag.moveTo(594, 352)

    @classmethod
    @_is_tooltip_visible
    def is_bank_tooltip_visible(cls):
        pass

    @classmethod
    @_is_tooltip_visible
    def is_inventory_tooltip_visible(cls):
        pass

    @staticmethod
    def screenshot_bank_tooltip_area():
        return ScreenCapture.custom_area((688, 527, 160, 30))

    @staticmethod
    def screenshot_inventory_tooltip_area():
        return ScreenCapture.custom_area((545, 305, 160, 29))

    @staticmethod
    def get_bank_tooltip_rectangle(tooltip_area: np.ndarray):
        tooltip_area = OCR.convert_to_grayscale(tooltip_area)
        tooltip_area = cv2.morphologyEx(tooltip_area, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        tooltip_area = OCR.invert_image(tooltip_area)

        threshold = 170
        max_threshold = 125
        while threshold >= max_threshold:
            binarized_tooltip_area = OCR.binarize_image(tooltip_area, threshold)
            canny = cv2.Canny(binarized_tooltip_area, 50, 150)
            contours, _ = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                epsilon = 0.05 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                x, y, w, h = cv2.boundingRect(approx)
                if w > 60 and h > 18:
                    return x, y, w, h
            threshold -=1
        return None

    @staticmethod
    def get_inventory_tooltip_rectangle(tooltip_area: np.ndarray):
        tooltip_area = OCR.convert_to_grayscale(tooltip_area)
        tooltip_area = OCR.invert_image(tooltip_area)

        threshold = 190
        max_threshold = 225
        while threshold <= max_threshold:
            binarized_tooltip_area = OCR.binarize_image(tooltip_area, threshold)
            canny = cv2.Canny(binarized_tooltip_area, 50, 150)
            contours, _ = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                epsilon = 0.05 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                x, y, w, h = cv2.boundingRect(approx)
                if w > 60 and h > 18:
                    return x, y, w, h
            threshold +=1
        return None

    @staticmethod
    def crop_tooltip_from_image(screenshot: np.ndarray, rectangle: tuple[int, int, int, int]):
        x, y, w, h = rectangle
        return screenshot[y:y+h, x:x+w]

    @classmethod
    def read_tooltip_text(cls, tooltip: np.ndarray):
        """
        For best results the `tooltip` has to be cropped out with 
        `crop_tooltip_from_image()`, which has to get its `rectangle`
        argument from `get_bank_tooltip_rectangle()'.
        """
        tooltip = OCR.convert_to_grayscale(tooltip)
        tooltip = OCR.invert_image(tooltip)
        tooltip = OCR.resize_image(tooltip, tooltip.shape[1] * 5, tooltip.shape[0] * 5)
        tooltip = OCR.dilate_image(tooltip, 2)

        binarization_value = 145
        while True:
            tooltip = OCR.binarize_image(tooltip, binarization_value)
            tooltip = cv2.GaussianBlur(tooltip, (3, 3), 0)
            text = OCR.get_text_from_image(tooltip)
            text = text.replace(" ", "")
            if re.match(r"\d+podsoutof\d+", text):
                return text
            binarization_value += 5
            if binarization_value > 255:
                log.critical("Failed to read tooltip text.")
                cls.save_images_for_debug()
                os._exit(1)

    @staticmethod
    def parse_tooltip_text(extracted_tooltip_text) -> tuple[int, int]:
        split_text = extracted_tooltip_text.split("podsoutof")
        numbers = []
        for text in split_text:
            text = text.strip()
            text = text.replace(" ", "")
            number = ""
            for char in text:
                if char.isdigit():
                    number += char
            numbers.append(int(number))
        return tuple(numbers)

    @classmethod
    def save_images_for_debug(cls):
        dir_path = "src\\bot\\states\\out_of_combat\\pods_reader\\reading_failed_images"
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        log.info("Capturing images for debugging ... ")
        game_window_screenshot = ScreenCapture.game_window()
        bank_tooltip_screeshot = cls.screenshot_bank_tooltip_area()
        inventory_tooltip_screenshot = cls.screenshot_inventory_tooltip_area()
        date_and_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log.info("Saving images ... ")
        cv2.imwrite(os.path.join(dir_path, f"game_window_{date_and_time}.png"), game_window_screenshot)
        cv2.imwrite(os.path.join(dir_path, f"bank_tooltip_{date_and_time}.png"), bank_tooltip_screeshot)
        cv2.imwrite(os.path.join(dir_path, f"inventory_tooltip_{date_and_time}.png"), inventory_tooltip_screenshot)
        log.info("Images saved.")

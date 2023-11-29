from time import perf_counter

from functools import wraps

import cv2
import numpy as np
import pyautogui as pyag

from src.ocr.ocr import OCR
from src.window_capture import WindowCapture


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
        raise Exception(f"Timed out while getting '{tooltip_name.capitalize()}' pods amount.")
    return wrapper


def _get_occupied_pods(decorated_method):
    @wraps(decorated_method)
    def wrapper(cls, *args, **kwargs):
        tooltip_name = decorated_method.__name__.split("_")[2]
        get_numbers = getattr(cls, f"get_{tooltip_name}_numbers")
        return get_numbers()[0]
    return wrapper


def _get_total_pods(decorated_method):
    @wraps(decorated_method)
    def wrapper(cls, *args, **kwargs):
        tooltip_name = decorated_method.__name__.split("_")[2]
        get_numbers = getattr(cls, f"get_{tooltip_name}_numbers")
        return get_numbers()[1]
    return wrapper


def _get_percentage(decorated_method):
    @wraps(decorated_method)
    def wrapper(cls, *args, **kwargs):
        tooltip_name = decorated_method.__name__.split("_")[2]
        get_numbers = getattr(cls, f"get_{tooltip_name}_numbers")
        occupied, total = get_numbers()
        return round(occupied / total * 100, 2)
    return wrapper


class PodsGetter:
    """
    For most methods in this class to work the according interface has to be open.
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
        return WindowCapture.custom_area_capture((688, 527, 160, 30))

    @staticmethod
    def screenshot_inventory_tooltip_area():
        return WindowCapture.custom_area_capture((545, 305, 160, 29))

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

    @staticmethod
    def read_tooltip_text(tooltip: np.ndarray):
        """
        For best results the `tooltip` has to be cropped out with 
        `crop_tooltip_from_image()`, which has to get its `rectangle`
        argument from `get_bank_tooltip_rectangle()'.
        """
        tooltip = OCR.convert_to_grayscale(tooltip)
        tooltip = OCR.invert_image(tooltip)
        tooltip = OCR.resize_image(tooltip, tooltip.shape[1] * 5, tooltip.shape[0] * 5)
        tooltip = OCR.dilate_image(tooltip, 2)
        tooltip = OCR.binarize_image(tooltip, 145)
        tooltip = cv2.GaussianBlur(tooltip, (3, 3), 0)
        return OCR.get_text_from_image(tooltip, ocr_engine="tesserocr")

    @staticmethod
    def parse_tooltip_text(extracted_tooltip_text) -> tuple[int, int]:
        split_text = extracted_tooltip_text.split("pods out of")
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

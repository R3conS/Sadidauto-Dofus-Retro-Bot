from src.logger import Logger
log = Logger.get_logger(Logger.DEBUG, True, True)

import re
from abc import ABC, abstractstaticmethod
from time import perf_counter

import cv2
import numpy as np

from src.bot._exceptions import RecoverableException
from src.utilities.ocr.ocr import OCR


class BaseReader(ABC):

    @abstractstaticmethod
    def _screenshot_tooltip_area() -> np.ndarray:
        pass

    @abstractstaticmethod
    def _trigger_tooltip():
        pass

    @abstractstaticmethod
    def _hide_tooltip():
        pass

    @abstractstaticmethod
    def _get_tooltip_rectangle(tooltip_area_image: np.ndarray) -> tuple[int, int, int, int]:
        pass

    @abstractstaticmethod
    def _read_tooltip_text(cropped_out_tooltip_image: np.ndarray) -> str:
        pass

    @classmethod
    def get_occupied_pods(cls) -> int:
        log.info("Getting occupied pods amount ...")
        numbers = cls._get_numbers()
        if numbers is None:
            raise RecoverableException("Failed to get occupied pods.")
        return numbers[0]

    @classmethod
    def get_total_pods(cls) -> int:
        log.info("Getting total pods amount ...")
        numbers = cls._get_numbers()
        if numbers is None:
            raise RecoverableException("Failed to get total pods.")
        return numbers[1]

    @classmethod
    def get_occupied_percentage(cls) -> float:
        log.info("Getting occupied pods percentage ...")
        numbers = cls._get_numbers()
        if numbers is None:
            raise RecoverableException("Failed to get occupied pods percentage.")
        return round(numbers[0] / numbers[1] * 100, 2)

    @classmethod
    def _get_numbers(cls) -> tuple[int, int]:
        """Get (pods_occupied, total_pods) numbers."""
        cls._trigger_tooltip()
        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if cls._is_tooltip_visible():
                tooltip_area = cls._screenshot_tooltip_area()
                tooltip_rectangle = cls._get_tooltip_rectangle(tooltip_area)
                cls._hide_tooltip()
                if tooltip_rectangle is not None:
                    tooltip = cls._crop_out_tooltip(tooltip_area, tooltip_rectangle)
                    text = cls._read_tooltip_text(tooltip)
                    return cls._parse_tooltip_text(text)
        # ToDo: Raise an unrecoverable exception if None when getting
        # bank numbers because the view of the tooltip shouldn't ever be 
        # obstructed by anything.
        return None

    @classmethod
    def _is_tooltip_visible(cls):
        if cls._get_tooltip_rectangle(cls._screenshot_tooltip_area()) is not None:
            return True

    @staticmethod
    def _crop_out_tooltip(tooltip_area_image: np.ndarray, rectangle: tuple[int, int, int, int]) -> np.ndarray:
        x, y, w, h = rectangle
        return tooltip_area_image[y:y+h, x:x+w]

    @staticmethod
    def _read_tooltip_text(tooltip: np.ndarray):
        """
        For best results the `tooltip` has to be cropped out with 
        `_crop_out_tooltip()`, which has to get its `rectangle`
        argument from `_get_tooltip_rectangle()'.
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
                raise RecoverableException(
                    f"Failed to read defined tooltip pattern. "
                    f"Received: '{text}'. "
                    f"Expected: '\d+podsoutof\d+'."
                )

    @staticmethod
    def _parse_tooltip_text(text: str) -> tuple[int, int]:
        split_text = text.split("podsoutof")
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

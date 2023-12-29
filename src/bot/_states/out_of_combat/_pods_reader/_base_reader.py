from src.logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from abc import ABC, abstractclassmethod, abstractstaticmethod

import cv2
import numpy as np
import os
import re

from src.ocr.ocr import OCR


class BaseReader(ABC):

    @abstractclassmethod
    def get_numbers(cls) -> tuple[int, int]:
        pass

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
        numbers = cls.get_numbers()
        if numbers is not None:
            return numbers[0]
        return None

    @classmethod
    def get_total_pods(cls) -> int:
        numbers = cls.get_numbers()
        if numbers is not None:
            return numbers[1]
        return None

    @classmethod
    def get_occupied_percentage(cls) -> float:
        numbers = cls.get_numbers()
        if numbers is not None:
            return round(numbers[0] / numbers[1] * 100, 2)
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
                log.critical("Failed to read tooltip text.")
                os._exit(1)

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

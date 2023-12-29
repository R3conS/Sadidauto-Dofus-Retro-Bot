from src.logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter

import cv2
import numpy as np
import pyautogui as pyag

from ._base_reader import BaseReader
from src.ocr.ocr import OCR
from src.screen_capture import ScreenCapture
from src.bot._exceptions import RecoverableException


class BankReader(BaseReader):

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
                tooltip = cls._crop_out_tooltip(tooltip_area, tooltip_rectangle)
                text = cls._read_tooltip_text(tooltip)
                return cls._parse_tooltip_text(text)
        log.error("Failed to get bank pods numbers.")
        return None

    @staticmethod
    def _screenshot_tooltip_area():
        return ScreenCapture.custom_area((688, 527, 160, 30))

    @staticmethod
    def _trigger_tooltip():
        pyag.moveTo(735, 560)

    @staticmethod
    def _hide_tooltip():
        pyag.moveTo(735, 580)

    @staticmethod
    def _get_tooltip_rectangle(tooltip_area: np.ndarray):
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
        raise RecoverableException("Failed to detect tooltip rectangle from bank tooltip area image.")

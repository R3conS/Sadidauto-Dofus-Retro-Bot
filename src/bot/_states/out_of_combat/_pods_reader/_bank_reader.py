from src.logger import Logger
log = Logger.get_logger(Logger.DEBUG, True, True)

from time import sleep

import cv2
import numpy as np
import pyautogui as pyag

from src.bot._exceptions import ExceptionReason, take_a_screenshot
from src.bot._states.out_of_combat._pods_reader._base_reader import BaseReader
from src.utilities.ocr.ocr import OCR
from src.utilities.screen_capture import ScreenCapture


class BankReader(BaseReader):

    @staticmethod
    def _screenshot_tooltip_area():
        return ScreenCapture.custom_area((688, 527, 160, 30))

    @staticmethod
    def _trigger_tooltip():
        pyag.moveTo(735, 560)

    @staticmethod
    def _hide_tooltip():
        pyag.moveTo(735, 580)

    @classmethod
    def _get_tooltip_rectangle(cls, tooltip_area: np.ndarray):
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

        log.error("Failed to get bank pods tooltip rectangle.")
        cls._trigger_tooltip()
        sleep(1) # Giving the tooltip some time to appear.
        take_a_screenshot(ExceptionReason.FAILED_TO_GET_BANK_PODS_TOOLTIP_RECTANGLE)

        return None

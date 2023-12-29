from src.logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import cv2
import numpy as np
import pyautogui as pyag

from ._base_reader import BaseReader
from src.ocr.ocr import OCR
from src.screen_capture import ScreenCapture


class InventoryReader(BaseReader):

    @staticmethod
    def _screenshot_tooltip_area():
        return ScreenCapture.custom_area((545, 305, 160, 29))

    @staticmethod
    def _trigger_tooltip():
        pyag.moveTo(594, 338)

    @staticmethod
    def _hide_tooltip():
        pyag.moveTo(594, 352)

    @staticmethod
    def _get_tooltip_rectangle(tooltip_area: np.ndarray):
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

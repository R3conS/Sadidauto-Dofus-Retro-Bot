from time import perf_counter

import cv2
import numpy as np
import pyautogui as pyag

from src.ocr.ocr import OCR
from src.window_capture import WindowCapture


class PodsGetter:

    @classmethod
    def get_pods_numbers(cls) -> tuple[int, int]:
        cls.trigger_pods_tooltip()
        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if cls.is_pods_tooltip_visible():
                tooltip_area = cls.screenshot_tooltip_area()
                tooltip_rectangle = cls.get_tooltip_rectangle_from_image(tooltip_area)
                cls.hide_pods_tooltip()
                if tooltip_rectangle is not None:
                    tooltip = cls.crop_tooltip_from_image(tooltip_area, tooltip_rectangle)
                    text = cls.read_text_from_tooltip(tooltip)
                    return cls.parse_tooltip_text(text)
        raise Exception(f"Timed out while getting pods amount.")

    @staticmethod
    def trigger_pods_tooltip():
        pyag.moveTo(735, 560)

    @staticmethod
    def hide_pods_tooltip():
        pyag.moveTo(735, 580)

    @classmethod
    def is_pods_tooltip_visible(cls):
        tooltip_area = cls.screenshot_tooltip_area()
        tooltip_rectangle = cls.get_tooltip_rectangle_from_image(tooltip_area)
        if tooltip_rectangle is not None:
            return True
        return False

    @staticmethod
    def screenshot_tooltip_area():
        return WindowCapture.custom_area_capture((688, 527, 160, 30))

    @staticmethod
    def get_tooltip_rectangle_from_image(tooltip_area: np.ndarray):
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
    def crop_tooltip_from_image(screenshot: np.ndarray, rectangle: tuple[int, int, int, int]):
        x, y, w, h = rectangle
        return screenshot[y:y+h, x:x+w]

    @staticmethod
    def read_text_from_tooltip(tooltip: np.ndarray):
        """
        For best results the `tooltip` has to be cropped out with 
        `crop_tooltip_from_image()`, which has to get its `rectangle`
        argument from `get_tooltip_rectangle_from_image()'.
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

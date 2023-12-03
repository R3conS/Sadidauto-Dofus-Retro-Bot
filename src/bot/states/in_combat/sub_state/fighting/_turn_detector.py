from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter

import numpy as np
import pyautogui as pyag

from src.ocr.ocr import OCR
from src.screen_capture import ScreenCapture
from .status_enum import Status


class TurnDetector:

    def __init__(self, character_name: str):
        self.character_name = character_name

    def detect_turn(self):
        start_time = perf_counter()
        while perf_counter() - start_time <= 120:
            if self.is_turn_illustration_visible():
                name_area_image = self.screenshot_name_area()
                name_area_image = self.preprocess_image(name_area_image)
                name = OCR.get_text_from_image(name_area_image, ocr_engine="tesserocr")
                print(name)
                if name is not None and name != "":
                    if name.strip() == self.character_name:
                        log.info("Successfully detected character's turn.")
                        return Status.SUCCESSFULLY_DETECTED_TURN
        else:
            log.info("Timed out while trying to detect character's turn.")
            return Status.TIMED_OUT_WHILE_DETECTING_TURN

    def is_turn_illustration_visible(self):
        pixels = {
            (407, 105): (249, 103, 1),
            (196, 98): (93, 85, 68),
            (306, 97): (90, 85, 69)
        }
        match_results = []
        for pixel, color in pixels.items():
            match_results.append(pyag.pixelMatchesColor(pixel[0], pixel[1], color, 5))
        return all(match_results)

    @staticmethod
    def screenshot_name_area() -> np.ndarray:
        return ScreenCapture.custom_area((188, 100, 210, 21))
    
    @staticmethod
    def preprocess_image(image: np.ndarray):
        image = OCR.convert_to_grayscale(image)
        image = OCR.resize_image(image, image.shape[1] * 2, image.shape[0] * 2)
        image = OCR.erode_image(image, 2)
        return OCR.binarize_image(image, 30)

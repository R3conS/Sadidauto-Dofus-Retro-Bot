from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter

import cv2
import numpy as np
import pyautogui as pyag

from src.ocr.ocr import OCR
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture
from src.utilities import load_image
from .status_enum import Status


class TurnDetector:

    image_folder_path = "src\\bot\\states\\in_combat\\sub_state\\fighting\\images"
    first_turn_indicator_image = load_image(image_folder_path, "first_turn_indicator.png")

    @classmethod
    def detect_start_of_turn(cls, character_name: str):
        start_time = perf_counter()
        while perf_counter() - start_time <= 120:
            if cls.is_turn_illustration_visible():
                name_area_image = cls.screenshot_name_area()
                name_area_image = cls.preprocess_image(name_area_image)
                name = OCR.get_text_from_image(name_area_image, ocr_engine="tesserocr")
                print(name)
                if name is not None and name != "":
                    if name.strip() == character_name:
                        log.info("Successfully detected character's turn.")
                        return Status.SUCCESSFULLY_DETECTED_TURN
        else:
            log.info("Timed out while trying to detect character's turn.")
            return Status.TIMED_OUT_WHILE_DETECTING_TURN

    @staticmethod
    def is_turn_illustration_visible():
        pixels = {
            (407, 105): (249, 103, 1),
            (196, 98): (93, 85, 68),
            (306, 97): (90, 85, 69)
        }
        match_results = []
        for pixel, color in pixels.items():
            match_results.append(pyag.pixelMatchesColor(pixel[0], pixel[1], color, 5))
        return all(match_results)

    @classmethod
    def is_first_turn(cls):
        return len(
            ImageDetection.find_image(
                haystack=cls.screenshot_turn_counter_area(),
                needle=cls.first_turn_indicator_image,
                confidence=0.98,
                method=cv2.TM_CCOEFF_NORMED,
            )
        ) > 0

    @staticmethod
    def screenshot_name_area() -> np.ndarray:
        return ScreenCapture.custom_area((188, 100, 210, 21))
    
    @staticmethod
    def screenshot_turn_counter_area() -> np.ndarray:
        return ScreenCapture.custom_area((905, 538, 31, 61))
    
    @staticmethod
    def preprocess_image(image: np.ndarray):
        image = OCR.convert_to_grayscale(image)
        image = OCR.resize_image(image, image.shape[1] * 2, image.shape[0] * 2)
        image = OCR.erode_image(image, 2)
        return OCR.binarize_image(image, 30)

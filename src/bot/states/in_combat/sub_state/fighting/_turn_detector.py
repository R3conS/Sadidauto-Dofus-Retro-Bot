from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter

import cv2
import numpy as np
import pyautogui as pyag

from src.ocr.ocr import OCR
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture
from src.utilities import load_image, move_mouse_off_game_area
from src.bot.states.in_combat.status_enum import Status


class TurnDetector:

    _IMAGE_FOLDER_PATH = "src\\bot\\states\\in_combat\\sub_state\\fighting\\images"
    _FIRST_TURN_INDICATOR_IMAGE = load_image(_IMAGE_FOLDER_PATH, "first_turn_indicator.png")
    _CLOSE_BUTTON_IMAGE = load_image(_IMAGE_FOLDER_PATH, "close_button.png")
    _DOFUS_LOGO_IMAGE = load_image(_IMAGE_FOLDER_PATH, "dofus_logo.png")
    _AP_COUNTER_IMAGE = load_image(_IMAGE_FOLDER_PATH, "ap_counter_image.png")
    _AP_COUNTER_IMAGE_MASK = ImageDetection.create_mask(_AP_COUNTER_IMAGE)

    @classmethod
    def detect_start_of_turn(cls, character_name: str):
        log.info("Waiting for character's turn ...")
        start_time = perf_counter()
        while perf_counter() - start_time <= 120:
            if (
                cls._is_character_turn_illustration_visible(character_name)
                or cls._is_turn_timer_filling_up()
            ):
                log.info("Successfully detected character's turn.")
                return Status.SUCCESSFULLY_DETECTED_TURN

            if not cls.is_ap_counter_visible():
                if cls._is_close_button_visible():
                    log.info("Detected 'Fight Results' window.")
                    return Status.FIGHT_RESULTS_WINDOW_DETECTED
                # If code reaches this point it most likely means that the
                # account got disconnected.
                log.error("Failed to detect AP counter while trying to detect character's turn.")
                return Status.FAILED_TO_DETECT_AP_COUNTER
            
        else:
            log.error("Timed out while trying to detect character's turn.")
            return Status.TIMED_OUT_WHILE_DETECTING_TURN

    @classmethod
    def pass_turn(cls, character_name: str):
        pyag.moveTo(618, 726)
        pyag.click()
        move_mouse_off_game_area()

        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if (
                not cls._is_character_turn_illustration_visible(character_name)
                and not cls._is_turn_timer_filling_up()
            ):
                log.info("Successfully passed turn.")
                return Status.SUCCESSFULLY_PASSED_TURN
        else:
            log.error("Timed out while detecting if turn was passed.")
            return Status.FAILED_TO_PASS_TURN

    @classmethod
    def is_first_turn(cls):
        return len(
            ImageDetection.find_image(
                haystack=cls._screenshot_turn_counter_area(),
                needle=cls._FIRST_TURN_INDICATOR_IMAGE,
                confidence=0.98,
                method=cv2.TM_CCOEFF_NORMED,
            )
        ) > 0

    @classmethod
    def is_ap_counter_visible(cls):
        return len(
            ImageDetection.find_image(
                haystack=ScreenCapture.custom_area((452, 598, 41, 48)),
                needle=cls._AP_COUNTER_IMAGE,
                confidence=0.99,
                mask=cls._AP_COUNTER_IMAGE_MASK
            )
        ) > 0

    @classmethod
    def _is_character_turn_illustration_visible(cls, character_name: str):
        if cls._is_turn_illustration_visible():
            name_area_image = cls._screenshot_name_area()
            name_area_image = cls._preprocess_image(name_area_image)
            name = OCR.get_text_from_image(name_area_image)
            if name is not None and name != "":
                if name.strip() == character_name:
                    return True
        return False

    @staticmethod
    def _is_turn_illustration_visible():
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
    def _screenshot_name_area() -> np.ndarray:
        return ScreenCapture.custom_area((188, 100, 210, 21))
    
    @staticmethod
    def _screenshot_turn_counter_area() -> np.ndarray:
        return ScreenCapture.custom_area((905, 538, 31, 61))
    
    @staticmethod
    def _preprocess_image(image: np.ndarray):
        image = OCR.convert_to_grayscale(image)
        image = OCR.resize_image(image, image.shape[1] * 2, image.shape[0] * 2)
        image = OCR.erode_image(image, 2)
        return OCR.binarize_image(image, 30)

    @classmethod
    def _is_close_button_visible(cls):
        # Detecting within a time frame because it takes some time for the game
        # to fully render/draw the button on the screen.
        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if len(
                ImageDetection.find_image(
                    haystack=ScreenCapture.game_window(),
                    needle=cls._CLOSE_BUTTON_IMAGE,
                    confidence=0.99,
                    method=cv2.TM_SQDIFF_NORMED,
                )
            ) > 0:
                return True
        return False

    @staticmethod
    def _is_turn_timer_filling_up():
        return pyag.pixelMatchesColor(542, 630, (255, 102, 0))

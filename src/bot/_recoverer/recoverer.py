from src.logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter

import cv2
import pyautogui as pyag

from src.screen_capture import ScreenCapture
from src.image_detection import ImageDetection
from src.ocr.ocr import OCR
from src.bot._exceptions import UnrecoverableException


class Recoverer:

    CHOOSE_A_SERVER_AREA = (59, 254, 233, 30)
    CHOOSE_YOUR_CHARACTER_AREA = (61, 300, 226, 32)
    SERVER_NAME_AREAS = [
        (83, 478, 135, 23),
        (243, 478, 135, 23),
        (403, 478, 135, 23),
        (563, 478, 135, 23),
        (723, 478, 135, 23)
    ]
    CHARACTER_NAME_AREAS = [
        (78, 531, 136, 23),
        (239, 531, 136, 23),
        (399, 532, 136, 23),
        (562, 531, 136, 23),
        (725, 531, 136, 23)
    ]

    def __init__(self, character_name: str, server_name: str):
        self._character_name = character_name
        self._server_name = server_name
    
    def recover(self):
        pass

    @classmethod
    def _is_choose_a_server_visible(cls):
        return OCR.get_text_from_image(
            ScreenCapture.custom_area(cls.CHOOSE_A_SERVER_AREA)
        ) == "Choose a server"

    @classmethod
    def _is_choose_your_character_visible(cls):
        return OCR.get_text_from_image(
            ScreenCapture.custom_area(cls.CHOOSE_YOUR_CHARACTER_AREA)
        ) == "Choose your character"

    @staticmethod
    def _read_server_name(name_area):
        area = ScreenCapture.custom_area(name_area)
        area = OCR.convert_to_grayscale(area)
        area = OCR.binarize_image(area, 215)
        area = OCR.resize_image(area, 200, 50)
        return OCR.get_text_from_image(area)

    @staticmethod
    def _read_character_name(name_area):
        area = ScreenCapture.custom_area(name_area)
        area = OCR.convert_to_grayscale(area)
        area = OCR.invert_image(area)
        area = OCR.resize_image(area, area.shape[1] * 3, area.shape[0] * 2)
        area = OCR.dilate_image(area, 2)
        area = OCR.binarize_image(area, 130)
        return OCR.get_text_from_image(area)

    def _choose_character(self):
        log.info(f"Looking for a character named: '{self._character_name}' ... ")
        for name_area in self.CHARACTER_NAME_AREAS:
            if self._read_character_name(name_area) == self._character_name:
                log.info(f"Character found! Selecting ... ")
                click_coords = ImageDetection.get_rectangle_center_point(name_area)
                pyag.moveTo(*click_coords)
                pyag.click(clicks=2, interval=0.1)

                timeout = 10
                start_time = perf_counter()
                while perf_counter() - start_time <= timeout:
                    if not self._is_choose_a_server_visible():
                        log.info("Successfully chose the character!")
                        return
                else:
                    raise UnrecoverableException(
                        "Timed out while choosing the character. "
                        f"Timeout: {timeout} seconds."
                    )
        raise UnrecoverableException(f"Couldn't find a character named: '{self._character_name}'!")

    def _choose_server(self):
        log.info(f"Looking for a server named: '{self._server_name}' ... ")
        for name_area in self.SERVER_NAME_AREAS:
            if self._read_server_name(name_area) == self._server_name:
                log.info(f"Server found! Selecting ... ")
                click_coords = ImageDetection.get_rectangle_center_point(name_area)
                pyag.moveTo(*click_coords)
                pyag.click(clicks=2, interval=0.1)
        
                timeout = 10
                start_time = perf_counter()
                while perf_counter() - start_time <= timeout:
                    # ToDo: Also check if the account gets logged in straight
                    # into the game. This happens when the character is in 
                    # combat and was disconnected during it.
                    if self._is_choose_your_character_visible():
                        log.info(f"Successfully chose server: '{self._server_name}'!")
                        return
                else:
                    raise UnrecoverableException(
                        "Timed out while choosing the server. "
                        f"Timeout: {timeout} seconds."
                    )
        raise UnrecoverableException(f"Couldn't find a server named: '{self._server_name}'!")


if __name__ == "__main__":
    recoverer = Recoverer("Longestnamepossibleh", "Semi-like")
    # recoverer._choose_server()
    # print(recoverer._read_character_name(recoverer.CHARACTER_NAME_AREAS[0]))
    # for name_area in recoverer.CHARACTER_NAME_AREAS:
    #     print(recoverer._read_character_name(name_area))
    # recoverer._choose_server()
    # recoverer._choose_character()

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

    def _choose_server(self):
        log.info("Choosing the server ... ")
        for name_area in self.SERVER_NAME_AREAS:
            if self._read_server_name(name_area) == self._server_name:
                click_coords = ImageDetection.get_rectangle_center_point(name_area)
                pyag.moveTo(*click_coords)
                pyag.click(clicks=2, interval=0.1)
        
                timeout = 10
                start_time = perf_counter()
                while perf_counter() - start_time <= timeout:
                    if self._is_choose_your_character_visible():
                        log.info("Successfully chose the server!")
                        return
                else:
                    raise UnrecoverableException(
                        "Timed out while choosing the server. "
                        f"Timeout: {timeout} seconds."
                    )
        raise UnrecoverableException(f"Couldn't find server with name '{self._server_name}'!")


if __name__ == "__main__":
    # print(Recoverer._is_choose_a_server_visible())
    # print(Recoverer._read_server_name(Recoverer.SERVER_NAME_AREAS["server_1"]))
    recoverer = Recoverer("Juni", "Semi-like")
    # print(recoverer._is_choose_a_server_visible())
    # print(recoverer._is_choose_your_character_visible())
    # print(recoverer._read_server_name(recoverer.SERVER_NAME_AREAS[0]))
    recoverer._choose_server()

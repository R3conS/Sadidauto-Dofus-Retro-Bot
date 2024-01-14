from src.logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter, sleep

import cv2
import numpy as np
import pyautogui as pyag

from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture
from src.ocr.ocr import OCR
from src.bot._exceptions import UnrecoverableException
from src.utilities import load_image_full_path


class Reader:

    # Dofus client size must be 1000x785 for areas to be accurate.
    NAME_AREAS = [
        (81, 534, 190, 28), 
        (250, 534, 190, 28),
        (419, 534, 190, 28),
        (589, 534, 190, 28),
        (763, 534, 190, 28)
    ]
    NAME_TOOLTIP_TRIGGER_POS = [
        (221, 559), (391, 559), (561, 559), (733, 559), (905, 559)
    ]
    NAME_TOOLTIP_DOTS_IMAGE = load_image_full_path(
        "src\\bot\\_recoverer\\_character_name_reader\\_images\\tooltip_dots.png"
    )
    FORBIDDEN_CHARACTERS = [
        ".", ",", ":", ";", "!", "?", "|", "/", "\\", "(", ")", "{", "}", "<", ">"
    ]

    @classmethod
    def preprocess_screenshot_for_OCR(cls, sc: np.ndarray):
        sc = OCR.resize_image(sc, sc.shape[1] * 10, sc.shape[0] * 10)
        sc = OCR.convert_to_grayscale(sc)
        sc = OCR.binarize_image(sc, 190)
        sc = OCR.invert_image(sc)
        sc = cv2.GaussianBlur(sc, (3, 3), 0)
        return sc
    
    @classmethod
    def read_name_area(cls, name_area, name_tooltip_trigger_pos):
        if cls.are_tooltip_dots_visible(name_area):
            cls.trigger_name_tooltip(name_area, name_tooltip_trigger_pos)
        sc = ScreenCapture.custom_area(name_area)
        sc = cls.preprocess_screenshot_for_OCR(sc)
        name = OCR.get_text_from_image(sc)
        name = name[:20] # Max character name length is 20.
        name = "".join([c for c in name if c not in cls.FORBIDDEN_CHARACTERS])
        return name.strip()

    def trigger_name_tooltip(name_area, name_tooltip_trigger_pos):
        sc_before = ScreenCapture.custom_area(name_area)
        timeout = 3
        start_time = perf_counter()
        while perf_counter() - start_time < timeout:
            pyag.moveTo(*name_tooltip_trigger_pos)
            sc_after = ScreenCapture.custom_area(name_area)
            if not np.array_equal(sc_before, sc_after):
                return
            sleep(0.1)
        raise UnrecoverableException(f"Failed to trigger name tooltip in {timeout} seconds.")

    @staticmethod
    def read_all_character_names():
        names = []
        for name, trigger_pos in zip(Reader.NAME_AREAS, Reader.NAME_TOOLTIP_TRIGGER_POS):
            names.append(Reader.read_name_area(name, trigger_pos))
        return names

    @classmethod
    def are_tooltip_dots_visible(cls, name_area):
        return len(
            ImageDetection.find_image(
                haystack=ScreenCapture.custom_area(name_area),
                needle=cls.NAME_TOOLTIP_DOTS_IMAGE,
                confidence=0.95
            )
        ) > 0


if __name__ == "__main__":
    # name = Reader.read_name_area(
    #     Reader.NAME_AREAS[3], Reader.NAME_TOOLTIP_TRIGGER_POS[3]
    # )
    names = Reader.read_all_character_names()
    print(names)
    # print(Reader.are_tooltip_dots_visible(Reader.NAME_AREAS[4]))

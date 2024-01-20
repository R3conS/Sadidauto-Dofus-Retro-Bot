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
from src.utilities import load_image_full_path, move_mouse_off_game_area


class Selector:

    # Dofus client size must be 1000x785 for areas to be accurate.
    # At certain client sizes some character's lower halves (like q, j, g etc.) 
    # on the name tooltip are being cut off which makes it impossible to read 
    # accurately. If a need arises to change the client size, make sure to 
    # choose one that fully displays the characters on the tooltip. Also
    # adjust all the coords in the CHAR_SLOT_INFO dict accordingly.
    CHAR_SLOT_INFO = {
        1: {
            "name_area_with_tooltip": (81, 534, 190, 28), 
            "name_area_no_tooltip": (81, 539, 145, 28),
            "level_area": (81, 561, 120, 25), 
            "tooltip_trigger_pos": (221, 559),
            "slot_pos": (151, 470)
        },
        2: {
            "name_area_with_tooltip": (250, 534, 190, 28), 
            "name_area_no_tooltip": (250, 539, 145, 28),
            "level_area": (250, 561, 120, 25), 
            "tooltip_trigger_pos": (391, 559),
            "slot_pos": (321, 470)
        },
        3: {
            "name_area_with_tooltip": (420, 534, 190, 28), 
            "name_area_no_tooltip": (420, 539, 145, 28),
            "level_area": (420, 561, 120, 25), 
            "tooltip_trigger_pos": (561, 559),
            "slot_pos": (491, 470)
        },
        4: {
            "name_area_with_tooltip": (589, 534, 190, 28), 
            "name_area_no_tooltip": (591, 539, 145, 28),
            "level_area": (589, 561, 120, 25), 
            "tooltip_trigger_pos": (733, 559),
            "slot_pos": (663, 470)
        },
        5: {
            "name_area_with_tooltip": (763, 534, 190, 28), 
            "name_area_no_tooltip": (763, 539, 145, 28),
            "level_area": (763, 561, 120, 25), 
            "tooltip_trigger_pos": (905, 559),
            "slot_pos": (835, 470)
        }
    }
    NAME_TOOLTIP_DOTS_IMAGE = load_image_full_path(
        "src\\bot\\_recoverer\\_character_selector\\_images\\tooltip_dots.png"
    )
    FORBIDDEN_CHARACTERS = [
        ".", ",", ":", ";", "!", "?", "|", "/", "\\", "(", ")", "{", "}", "<", ">", " "
    ]

    def __init__(self, character_name: str, character_level: int):
        self._character_name = character_name
        self._character_level = character_level

    def select_character(self):
        log.info(f"Attempting to select character: '{self._character_name}' ... ")
        slot_pos = self._find_character_by_full_name()
        if slot_pos is None:
            slot_pos = self._find_character_by_partial_name()
        if slot_pos is None:
            raise UnrecoverableException(f"Failed to select character.")
        log.info(f"Double clicking character slot ... ")
        pyag.moveTo(*slot_pos)
        pyag.click(clicks=2, interval=0.1)
        self._wait_loading_screen_end()
        log.info(f"Character selected successfully.")

    def _find_character_by_full_name(self):
        log.info(f"Searching for character by full name ... ")
        for char_slot in range(1, len(self.CHAR_SLOT_INFO) + 1):
            if self._character_name == self._read_name_area(char_slot, read_tooltip=True):
                log.info(f"Found character at slot: '{char_slot}'.")
                return self.CHAR_SLOT_INFO[char_slot]["slot_pos"]
        log.error(f"Failed to find character by full name.")
        return None

    def _find_character_by_partial_name(self):
        """
        Finds the character by reading the name (without the tooltip) and
        level areas. This is a fallback method in case the tooltip cannot be 
        read properly, which happens quite often due to letters like 
        'q', 'j', 'g'.
        """
        log.info(f"Searching for character by partial name and level ... ")
        for char_slot in range(1, len(self.CHAR_SLOT_INFO) + 1):
            if (
                self._character_name[:9] in self._read_name_area(char_slot, read_tooltip=False)
                and self._character_level >= self._read_level_area(char_slot)
            ):
                log.info(f"Found character at slot: '{char_slot}'.")
                return self.CHAR_SLOT_INFO[char_slot]["slot_pos"]
        log.error(f"Failed to find character by partial name.")
        return None

    @classmethod
    def _read_name_area(cls, char_slot: int, read_tooltip: bool):
        if read_tooltip and cls._are_name_tooltip_dots_visible(char_slot):
            cls._trigger_name_tooltip(char_slot)
            sc = ScreenCapture.custom_area(cls.CHAR_SLOT_INFO[char_slot]["name_area_with_tooltip"])
            move_mouse_off_game_area() # Untrigger tooltip.
            sc = OCR.resize_image(sc, sc.shape[1] * 10, sc.shape[0] * 10)
            sc = OCR.convert_to_grayscale(sc)
            sc = OCR.binarize_image(sc, 190)
            sc = OCR.invert_image(sc)
            sc = cv2.GaussianBlur(sc, (3, 3), 0)
        else:
            sc = ScreenCapture.custom_area(cls.CHAR_SLOT_INFO[char_slot]["name_area_no_tooltip"])
            sc = OCR.convert_to_grayscale(sc)
            sc = OCR.invert_image(sc)
            sc = OCR.resize_image(sc, sc.shape[1] * 3, sc.shape[0] * 3)
            sc = OCR.binarize_image(sc, 130)
            sc = cv2.GaussianBlur(sc, (3, 3), 0)

        name = OCR.get_text_from_image(sc)
        name = name[:21] # Max character name length is 20.
        name = "".join([c for c in name if c not in cls.FORBIDDEN_CHARACTERS])
        return name.strip()

    @classmethod
    def _read_level_area(cls, char_slot: int):
        area = ScreenCapture.custom_area(cls.CHAR_SLOT_INFO[char_slot]["level_area"])
        area = OCR.convert_to_grayscale(area)
        area = OCR.invert_image(area)
        area = OCR.resize_image(area, area.shape[1] * 3, area.shape[0] * 3)
        area = OCR.dilate_image(area, 2)
        area = OCR.binarize_image(area, 110)
        text = OCR.get_text_from_image(area)
        if text == "":
            return None
        return int(text.split(" ")[-1].strip())

    @classmethod
    def _trigger_name_tooltip(cls, char_slot: int):
        sc_before = ScreenCapture.custom_area(cls.CHAR_SLOT_INFO[char_slot]["name_area_no_tooltip"])
        timeout = 4
        start_time = perf_counter()
        while perf_counter() - start_time < timeout:
            pyag.moveTo(*cls.CHAR_SLOT_INFO[char_slot]["tooltip_trigger_pos"])
            sc_after = ScreenCapture.custom_area(cls.CHAR_SLOT_INFO[char_slot]["name_area_no_tooltip"])
            if not np.array_equal(sc_before, sc_after):
                return
            sleep(0.1)
        raise UnrecoverableException(f"Failed to trigger name tooltip in {timeout} seconds.")

    @classmethod
    def _are_name_tooltip_dots_visible(cls, char_slot: int):
        return len(
            ImageDetection.find_image(
                haystack=ScreenCapture.custom_area(cls.CHAR_SLOT_INFO[char_slot]["name_area_no_tooltip"]),
                needle=cls.NAME_TOOLTIP_DOTS_IMAGE,
                confidence=0.95
            )
        ) > 0

    @staticmethod
    def _wait_loading_screen_end():
        log.info(f"Waiting for the loading screen to end ... ")
        timeout = 20
        start_time = perf_counter()
        while perf_counter() - start_time < timeout:
            if pyag.pixelMatchesColor(636, 753, (213, 207, 170)):
                log.info(f"Loading screen has ended.")
                return
            sleep(0.1)
        raise UnrecoverableException(
            "Failed to detect end of loading screen. "
            f"Timed out: {timeout} seconds."
        )


if __name__ == "__main__":
    selector = Selector("Juni", 65)
    selector.select_character()

from src.logger import get_logger

log = get_logger()

from time import perf_counter, sleep

import cv2
import numpy as np
import pyautogui as pyag

from src.bot._exceptions import RecoverableException, UnrecoverableException
from src.bot._recoverer._reconnecter._game_window import get_game_window, resize_game_window
from src.utilities.general import load_image_full_path, move_mouse_off_game_area
from src.utilities.image_detection import ImageDetection
from src.utilities.ocr.ocr import OCR
from src.utilities.screen_capture import ScreenCapture


class CharacterSelector:

    # Dofus client size must be 1000x785 for search areas to be accurate.
    # At certain client sizes some character's lower halves (like q, j, g etc.) 
    # on the name tooltip are being cut off which makes it impossible to read 
    # accurately. If a need arises to change the client size, make sure to 
    # choose one that fully displays the characters on the tooltip. Also
    # adjust all the coords in the CHAR_SLOT_INFO dict accordingly.
    WINDOW_SIZE = (1000, 785)
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
        "src\\bot\\_recoverer\\_reconnecter\\_images\\tooltip_dots.png"
    )
    FORBIDDEN_CHARACTERS = [
        ".", ",", ":", ";", "!", "?", "|", "/", "\\", "(", ")", "{", "}", "<", ">", " "
    ]

    def __init__(
        self, 
        character_name: str, 
        character_level: int,
        game_window_identifier: int | str, # hwnd (int) or title (str).
    ):
        self._character_name = character_name
        self._character_level = character_level
        self._game_window = get_game_window(game_window_identifier)

    def select_character(self):
        log.info("Attempting to select the character ...")
        if self._game_window.size != self.WINDOW_SIZE:
            resize_game_window(self._game_window, self.WINDOW_SIZE)
        slot_pos = self._find_character_by_full_name()
        if slot_pos is None:
            slot_pos = self._find_character_by_partial_name()
        if slot_pos is None:
            raise RecoverableException("Failed to select the character.")
        log.info("Double clicking the character slot ... ")
        pyag.moveTo(*slot_pos)
        pyag.click(clicks=2, interval=0.1)
        self._wait_loading_screen_end()
        log.info("Successfully selected the character!")
        move_mouse_off_game_area()

    @staticmethod
    def is_on_character_selection_screen():
        return OCR.get_text_from_image(
            ScreenCapture.custom_area((61, 297, 246, 32))
        ) == "Choose your character"

    def _find_character_by_full_name(self):
        log.info("Searching for character by full name ... ")
        for char_slot in range(1, len(self.CHAR_SLOT_INFO) + 1):
            if self._character_name == self._read_name_area(char_slot, read_tooltip=True):
                log.info(f"Found character at slot: '{char_slot}'.")
                return self.CHAR_SLOT_INFO[char_slot]["slot_pos"]
        log.error("Failed to find character by full name.")
        return None

    def _find_character_by_partial_name(self):
        """
        Finds the character by reading the name (without the tooltip) and
        level areas. This is a fallback method in case the tooltip cannot be 
        read properly, which happens quite often due to letters like 
        'q', 'j', 'g'.
        """
        log.info("Searching for character by partial name and level ... ")
        for char_slot in range(1, len(self.CHAR_SLOT_INFO) + 1):
            if (
                self._character_name[:9] in self._read_name_area(char_slot, read_tooltip=False)
                and self._character_level >= self._read_level_area(char_slot)
            ):
                log.info(f"Found character at slot: '{char_slot}'.")
                return self.CHAR_SLOT_INFO[char_slot]["slot_pos"]
        log.error("Failed to find character by partial name.")
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

    @classmethod
    def _wait_loading_screen_end(cls):
        log.info("Waiting for the loading screen to end ... ")
        timeout = 15
        start_time = perf_counter()
        while perf_counter() - start_time < timeout:
            if cls._is_control_area_visible():
                log.info("Loading screen has ended.")
                return
            sleep(0.25)
        raise RecoverableException(
            "Failed to detect end of loading screen. "
            f"Timed out: {timeout} seconds."
        )

    @staticmethod
    def _is_control_area_visible():
        """Chat, minimap, interface icons, spell/item bar etc."""
        return (
            pyag.pixelMatchesColor(673, 747, (213, 207, 170))
            # Color is different when an offer (exchange, group invite, etc.) is on screen.
            or pyag.pixelMatchesColor(673, 747, (192, 186, 153))
        )


if __name__ == "__main__":
    selector = CharacterSelector("Juni", 65, "Abrak")
    selector.select_character()

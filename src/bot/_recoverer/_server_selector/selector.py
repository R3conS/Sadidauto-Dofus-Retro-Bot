from src.logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter, sleep

import pyautogui as pyag

from src.utilities.screen_capture import ScreenCapture
from src.utilities.image_detection import ImageDetection
from src.utilities.ocr.ocr import OCR
from src.utilities.general import move_mouse_off_game_area
from src.bot._exceptions import UnrecoverableException


class Selector:

    # Dofus client size must be 1000x785 for areas to be accurate.
    SERVER_SLOTS = { # server_slot: server_name_area
        1: (88, 482, 138, 23),
        2: (257, 482, 138, 23),
        3: (425, 482, 138, 23),
        4: (594, 482, 138, 23),
        5: (763, 482, 138, 23)
    }

    def __init__(self, server_name: str):
        self._server_name = server_name
    
    def select_server(self):
        log.info(f"Attemping to select the server ...")
        slot_pos = self._find_server()
        if slot_pos is None:
            raise UnrecoverableException(f"Failed to select the server.")
        log.info(f"Double clicking the server slot ... ")
        pyag.moveTo(*slot_pos)
        pyag.click(clicks=2, interval=0.1)
        self._wait_loading_screen_end()
        log.info(f"Server selected successfully.")
        move_mouse_off_game_area()

    def _find_server(self):
        log.info(f"Looking for a server named: '{self._server_name}' ... ")
        for server_slot in range(1, len(self.SERVER_SLOTS) + 1):
            if self._server_name == self._read_server_name(server_slot):
                log.info(f"Found server at slot: '{server_slot}'.")
                return ImageDetection.get_rectangle_center_point(self.SERVER_SLOTS[server_slot])
        log.error(f"Failed to find the server.")
        return None

    @classmethod
    def _read_server_name(cls, server_slot: int):
        sc = ScreenCapture.custom_area(cls.SERVER_SLOTS[server_slot])
        sc = OCR.convert_to_grayscale(sc)
        sc = OCR.resize_image(sc, sc.shape[1] * 2, sc.shape[0] * 2)
        sc = OCR.binarize_image(sc, 200)
        sc = OCR.invert_image(sc)
        return OCR.get_text_from_image(sc).strip()

    @classmethod
    def _wait_loading_screen_end(cls):
        log.info(f"Waiting for the loading screen to end ... ")
        timeout = 20
        start_time = perf_counter()
        while perf_counter() - start_time < timeout:
            if (
                cls._is_character_selection_screen_visible()
                # Character selection screen is skipped if character is in combat.
                or cls._is_character_logged_in() 
            ):
                log.info(f"Loading screen has ended.")
                return
            sleep(0.1)
        raise UnrecoverableException(
            "Failed to detect end of loading screen. "
            f"Timed out: {timeout} seconds."
        )

    @staticmethod
    def _is_character_selection_screen_visible():
        return OCR.get_text_from_image(
            ScreenCapture.custom_area((61, 296, 248, 32))
        ) == "Choose your character"

    @staticmethod
    def _is_character_logged_in():
        return pyag.pixelMatchesColor(673, 747, (213, 207, 170))


if __name__ == "__main__":
    selector = Selector("Semi-like")
    selector.select_server()

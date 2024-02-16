from src.logger import get_logger

log = get_logger()

from time import perf_counter, sleep

import pyautogui as pyag

from src.bot._exceptions import RecoverableException
from src.bot._recoverer._reconnecter._game_window import get_game_window, resize_game_window
from src.utilities.general import move_mouse_off_game_area
from src.utilities.image_detection import ImageDetection
from src.utilities.ocr.ocr import OCR
from src.utilities.screen_capture import ScreenCapture


class ServerSelector:

    # Dofus client size must be 1000x785 for search areas to be accurate.
    WINDOW_SIZE = (1000, 785)
    SERVER_SLOTS = { # server_slot: server_name_area
        1: (88, 482, 138, 23),
        2: (257, 482, 138, 23),
        3: (425, 482, 138, 23),
        4: (594, 482, 138, 23),
        5: (763, 482, 138, 23)
    }

    def __init__(
        self, 
        server_name: str,
        game_window_identifier: int | str, # hwnd (int) or title (str).
    ):
        self._server_name = server_name
        self._game_window = get_game_window(game_window_identifier)
    
    def select_server(self):
        log.info("Attemping to select the server ...")
        if self._game_window.size != self.WINDOW_SIZE:
            resize_game_window(self._game_window, self.WINDOW_SIZE)
        slot_pos = self._find_server()
        log.info("Double clicking the server slot ... ")
        pyag.moveTo(*slot_pos)
        pyag.click(clicks=2, interval=0.1)
        self._wait_loading_screen_end()
        move_mouse_off_game_area()
        log.info("Successfully selected the server!")

    @staticmethod
    def is_on_server_selection_screen():
        return OCR.get_text_from_image(
            ScreenCapture.custom_area((62, 253, 227, 31))
        ) == "Choose a server"

    def _find_server(self):
        log.info(f"Looking for a server named: '{self._server_name}' ... ")
        for server_slot in range(1, len(self.SERVER_SLOTS) + 1):
            if self._server_name == self._read_server_name(server_slot):
                log.info(f"Found server at slot: '{server_slot}'.")
                return ImageDetection.get_rectangle_center_point(self.SERVER_SLOTS[server_slot])
        raise RecoverableException("Failed to find the server.")

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
        log.info("Waiting for the loading screen to end ... ")
        timeout = 15
        start_time = perf_counter()
        while perf_counter() - start_time < timeout:
            if (
                cls._is_on_character_selection_screen()
                # Character selection screen is skipped if character is in combat.
                or cls._is_control_area_visible() 
            ):
                log.info("Loading screen has ended.")
                return
            sleep(0.25)
        raise RecoverableException(
            "Failed to detect end of loading screen. "
            f"Timed out: {timeout} seconds."
        )

    @staticmethod
    def _is_on_character_selection_screen():
        return OCR.get_text_from_image(
            ScreenCapture.custom_area((61, 297, 246, 32))
        ) == "Choose your character"

    @staticmethod
    def _is_control_area_visible():
        """Chat, minimap, interface icons, spell/item bar etc."""
        return pyag.pixelMatchesColor(673, 747, (213, 207, 170))


if __name__ == "__main__":
    selector = ServerSelector("Boune", "Dofus Retro")
    selector.select_server()

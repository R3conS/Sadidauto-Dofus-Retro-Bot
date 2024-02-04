from src.logger import Logger
log = Logger.get_logger()

from time import perf_counter, sleep

import pyautogui as pyag

from src.bot._exceptions import RecoverableException, UnrecoverableException
from src.bot._interfaces.interfaces import Interfaces
from src.bot._recoverer._reconnecter._game_window import get_game_window, resize_game_window
from src.utilities.general import load_image_full_path
from src.utilities.image_detection import ImageDetection
from src.utilities.ocr.ocr import OCR
from src.utilities.screen_capture import ScreenCapture


class LoginClicker:

    # Dofus client size must be 1000x785 for search areas to be accurate.
    WINDOW_SIZE = (1000, 785)
    LOGIN_BUTTON_IMAGE = load_image_full_path("src\\bot\\_recoverer\\_reconnecter\\_images\\login_button.png")

    def __init__(
        self, 
        game_window_identifier: int | str # hwnd (int) or title (str).
    ):
        self._game_window = get_game_window(game_window_identifier)

    def login(self):
        log.info("Attempting to log in ...")
        if self._game_window.size != self.WINDOW_SIZE:
            resize_game_window(self._game_window, self.WINDOW_SIZE)

        if Interfaces.CONNECTION.is_open():
            log.info("Connecting via 'Connection' interface ...")
            Interfaces.CONNECTION.click_yes()
        elif self._is_login_button_visible():
            log.info("Connecting via 'Log in' button ...")
            pyag.moveTo(*self._get_login_button_pos())
            pyag.click()
        else:
            raise UnrecoverableException(
                "Failed to log in because neither 'Connection' interface "
                "is open nor is the 'Log in' button visible."
            )
        self._wait_loading_screen_pass()
        log.info("Successfully logged in!")

    @classmethod
    def is_on_login_screen(cls):
        return Interfaces.CONNECTION.is_open() or cls._is_login_button_visible()

    @staticmethod
    def _is_on_server_selection_screen():
        return OCR.get_text_from_image(
            ScreenCapture.custom_area((62, 244, 227, 31))
        ) == "Choose a server"

    @classmethod
    def _is_login_button_visible(cls):
        return len(
            ImageDetection.find_image(
                haystack=ScreenCapture.game_window(),
                needle=cls.LOGIN_BUTTON_IMAGE,
                confidence=0.95,
            )
        ) > 0

    @classmethod
    def _get_login_button_pos(cls):
        return ImageDetection.get_rectangle_center_point(
            ImageDetection.find_image(
                haystack=ScreenCapture.game_window(),
                needle=cls.LOGIN_BUTTON_IMAGE,
                confidence=0.95
            )
        )

    @classmethod
    def _wait_loading_screen_pass(cls):
        log.info("Waiting for the loading screen to pass ...")
        timeout = 15
        start_time = perf_counter()
        while perf_counter() - start_time < timeout:
            if cls._is_on_server_selection_screen():
                log.info("Loading screen passed!")
                return
            sleep(0.25)
        raise RecoverableException(
            "Failed to detect server selection screen. "
            f"Timed out: {timeout} seconds."
        )


if __name__ == "__main__":
    clicker = LoginClicker("Dofus Retro")
    clicker.login()
    
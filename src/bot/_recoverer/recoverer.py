from src.logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter, sleep

import pyautogui as pyag
import pygetwindow as gw

from src.screen_capture import ScreenCapture
from src.image_detection import ImageDetection
from src.ocr.ocr import OCR
from src.utilities import load_image
from src.bot._exceptions import UnrecoverableException
from src.bot._interfaces.interfaces import Interfaces
from src.bot._recoverer._character_selector.selector import Selector as CharacterSelector
from src.bot._recoverer._server_selector.selector import Selector as ServerSelector
from src.bot._states.states_enum import State as BotState


class Recoverer:

    WINDOW_SIZE_FOR_SERVER_AND_CHAR_SELECTION = (1000, 785)
    IMAGE_FOLDER_PATH = "src\\bot\\_recoverer\\_images"
    LOGIN_BUTTON_IMAGE = load_image(IMAGE_FOLDER_PATH, "login_button.png")
    BOT_STATE_DETERMINER_IMAGE = load_image(IMAGE_FOLDER_PATH, "bot_state_determiner.png")

    def __init__(
            self, 
            character_name: str, 
            server_name: str, 
            character_level: int,
            game_window_identifier: int | str, # String (title) only used for dev/testing.
            game_window_default_size: tuple[int, int]
        ):
        self._character_name = character_name
        self._server_name = server_name
        self._character_level = character_level
        self._game_window = self._get_game_window(game_window_identifier)
        self._game_window_default_size = game_window_default_size
        self._server_selector = ServerSelector(server_name)
        self._character_selector = CharacterSelector(character_name, character_level)

    def recover(self):
        if not self._is_character_logged_in():
            self._login()
            return self._determine_bot_state()
        Interfaces.close_all()
        return self._determine_bot_state()

    def _is_character_logged_in(self):
        return (
            pyag.pixelMatchesColor(673, 747, (213, 207, 170))
            # Color is different when an offer (exchange, group invite, etc.) is on screen.
            or pyag.pixelMatchesColor(673, 747, (192, 186, 153))
        )

    def _login(self):
        log.info("Attempting to log in ... ")
        if Interfaces.CONNECTION.is_open():
            log.info("Connecting via the 'Connection' interface ... ")
            Interfaces.CONNECTION.click_yes()
        elif self._is_login_button_visible():
            log.info("Connecting via the 'Log in' button ... ")
            pyag.moveTo(*self._get_login_button_pos())
            pyag.click()
        else:
            raise UnrecoverableException(
                "Failed to log in the character because neither 'Connection' "
                "interface is open nor is the 'Log in' button visible."
            )

        self._wait_loading_screen_end()
        self._resize_game_window(self.WINDOW_SIZE_FOR_SERVER_AND_CHAR_SELECTION)
        self._server_selector.select_server()
        # Character selection screen is skipped if character is in combat.
        if self._is_character_logged_in():
            log.info(f"Succesfully logged in")
            self._resize_game_window(self._game_window_default_size)
            return
        self._character_selector.select_character()
        if self._is_character_logged_in():
            log.info(f"Succesfully logged in.")
            self._resize_game_window(self._game_window_default_size)
            return

    def _resize_game_window(self, size: tuple[int, int]):
        log.info(f"Resizing game window to: {size}.")
        self._game_window.resizeTo(*size)

    @classmethod
    def _determine_bot_state(cls):
        if len(
            ImageDetection.find_image(
                haystack=ScreenCapture.custom_area((456, 595, 31, 22)),
                needle=cls.BOT_STATE_DETERMINER_IMAGE,
                confidence=0.95,
            )
        ) > 0:
            return BotState.IN_COMBAT
        return BotState.OUT_OF_COMBAT

    @staticmethod
    def _get_game_window(game_window_identifier: int | str):
        """Can be either a window handle (int) or a window title (str)."""
        if isinstance(game_window_identifier, int):
            return gw.Win32Window(game_window_identifier)
        elif isinstance(game_window_identifier, str):
            try:
                return gw.getWindowsWithTitle(game_window_identifier)[0]
            except IndexError:
                raise UnrecoverableException(f"Couldn't find window with title '{game_window_identifier}'!")
        else:
            raise UnrecoverableException("Invalid 'game_window_identifier' type!")

    @classmethod
    def _wait_loading_screen_end(cls):
        log.info(f"Waiting for the loading screen to end ... ")
        timeout = 30
        start_time = perf_counter()
        while perf_counter() - start_time < timeout:
            if cls._is_server_selection_screen_visible():
                log.info(f"Loading screen has ended.")
                return
            sleep(0.1)
        raise UnrecoverableException(
            "Failed to detect end of the loading screen. "
            f"Timed out: {timeout} seconds."
        )

    @staticmethod
    def _is_server_selection_screen_visible():
        return OCR.get_text_from_image(
            ScreenCapture.custom_area((62, 253, 227, 31))
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
                confidence=0.95,
            )
        )


if __name__ == "__main__":
    recoverer = Recoverer("Juni", "Semi-like", 65, "Abrak", (950, 785))
    recoverer._login()

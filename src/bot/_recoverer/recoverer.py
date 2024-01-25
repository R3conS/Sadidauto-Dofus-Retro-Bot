from src.logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter, sleep

import numpy as np
import pyautogui as pyag
import pygetwindow as gw

from src.utilities.screen_capture import ScreenCapture
from src.utilities.image_detection import ImageDetection
from src.utilities.ocr.ocr import OCR
from src.utilities.general import load_image
from src.bot._exceptions import UnrecoverableException, ExceptionReason
from src.bot._interfaces.interfaces import Interfaces
from src.bot._recoverer._character_selector.selector import Selector as CharacterSelector
from src.bot._recoverer._server_selector.selector import Selector as ServerSelector


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

    def recover(self, exception_reason: ExceptionReason = None):
        log.info(f"Attempting to recover ... ")
        if exception_reason == ExceptionReason.FAILED_TO_GET_MAP_COORDS:
            if not self._is_control_area_visible():
                self._login()
                return
            raise UnrecoverableException("Failed to get map coords because the map image is missing.")
        
        if not self._is_control_area_visible():
            self._login()
            return
        Interfaces.close_all()

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
                "Failed to log in because neither 'Connection' interface "
                "is open nor is the 'Log in' button visible."
            )

        self._wait_for_server_selection_screen()
        self._resize_game_window(self.WINDOW_SIZE_FOR_SERVER_AND_CHAR_SELECTION)
        
        self._server_selector.select_server()
        # Character selection screen is skipped if character is in combat.
        if self._is_control_area_visible():
            self._resize_game_window(self._game_window_default_size)
            self._wait_for_map_and_minimap_to_load()
            log.info(f"Succesfully logged in")
            return
        
        self._character_selector.select_character()
        if self._is_control_area_visible():
            self._resize_game_window(self._game_window_default_size)
            self._wait_for_map_and_minimap_to_load()
            log.info(f"Succesfully logged in")
            return

    def _resize_game_window(self, size: tuple[int, int]):
        log.info(f"Resizing game window to: {size}.")
        self._game_window.resizeTo(*size)
        # Putting the window back to most top left corner. After resizing
        # it's for some reason slightly moved off the left side of the screen.
        self._game_window.moveTo(-8, 0)

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
    def _get_login_button_pos(cls):
        return ImageDetection.get_rectangle_center_point(
            ImageDetection.find_image(
                haystack=ScreenCapture.game_window(),
                needle=cls.LOGIN_BUTTON_IMAGE,
                confidence=0.95,
            )
        )

    @classmethod
    def _wait_for_server_selection_screen(cls):
        log.info(f"Waiting for the server selection screen to load ... ")
        timeout = 30
        start_time = perf_counter()
        while perf_counter() - start_time < timeout:
            if cls._is_server_selection_screen_visible():
                log.info(f"Server selection screen has loaded.")
                return
            sleep(0.25)
        raise UnrecoverableException(
            "Failed to detect server selection screen. "
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

    @staticmethod
    def _is_control_area_visible():
        """Chat, minimap, interface icons, spell/item bar etc."""
        return (
            pyag.pixelMatchesColor(673, 747, (213, 207, 170))
            # Color is different when an offer (exchange, group invite, etc.) is on screen.
            or pyag.pixelMatchesColor(673, 747, (192, 186, 153))
        )

    @staticmethod
    def _has_map_loaded():
        """
        Map is the game area where the character can move around. It's 
        considered loaded when there is at least one non-black pixel in
        the search areas.
        """
        sc = ScreenCapture.game_window()
        search_areas = [
            sc[90:170, 5:900], # (x5, y90, w900, h170)
            sc[450:530, 5:900], # (x5, y450, w900, h170)
            sc[90:500, 5:150] # (x5, y90, w150, h500)
        ]
        for area in search_areas:
            if np.any(area != 0):
                return True
        return False

    @staticmethod
    def _has_minimap_loaded():
        sc = ScreenCapture.game_window()
        pixels = [ # sc[y, x]
            sc[667, 501],
            sc[667, 548],
            sc[692, 501],
            sc[692, 548]
        ]
        return any(np.all(pixel[::-1] != (242, 144, 110)) for pixel in pixels)

    @classmethod
    def _wait_for_map_and_minimap_to_load(cls):
        log.info("Waiting for the map and minimap to load ... ")
        timeout = 30
        start_time = perf_counter()
        while perf_counter() - start_time < timeout:
            if cls._has_map_loaded() and cls._has_minimap_loaded():
                log.info("Map and minimap have loaded.")
                return
            sleep(0.25)
        raise UnrecoverableException(
            "Failed to detect if map and minimap have loaded. "
            f"Timed out: {timeout} seconds."
        )


if __name__ == "__main__":
    # recoverer = Recoverer("Kofas", "Boune", 65, "Dofus Retro", (950, 785))
    recoverer = Recoverer("Juni", "Semi-like", 65, "Abrak", (950, 785))
    recoverer._login()

from src.logger import Logger
log = Logger.get_logger(Logger.DEBUG, True, True)

from cv2 import TM_CCOEFF_NORMED

from src.bot._exceptions import RecoverableException
from src.bot._interfaces._interface import Interface
from src.utilities.general import load_image
from src.utilities.image_detection import ImageDetection
from src.utilities.screen_capture import ScreenCapture


class MainMenu:
    """Appears when ESC is pressed or when X icon is clicked at the top right corner."""

    IMAGE_DIR_PATH = "src\\bot\\_interfaces\\_main_menu\\_images"
    MAIN_MENU_TITLE_IMAGES = [
        load_image(IMAGE_DIR_PATH, "main_menu_title_950x785.png"),
        load_image(IMAGE_DIR_PATH, "main_menu_title_1000x785.png")
    ]
    MAIN_MENU_CROSS_AREA = (850, 0, 140, 85)
    MAIN_MENU_CROSS_IMAGES = [
        load_image(IMAGE_DIR_PATH, "main_menu_cross_950x785.png"),
        load_image(IMAGE_DIR_PATH, "main_menu_cross_1000x785.png")
    ]
    CANCEL_BUTTON_IMAGES = [
        load_image(IMAGE_DIR_PATH, "cancel_button_950x785.png"),
        load_image(IMAGE_DIR_PATH, "cancel_button_1000x785.png")
    ]
    LOGOUT_BUTTON_IMAGES = [
        load_image(IMAGE_DIR_PATH, "logout_button_950x785.png"),
        load_image(IMAGE_DIR_PATH, "logout_button_1000x785.png")
    ]

    def __init__(self):
        self._name = "Main Menu"
        self._interface = Interface(self._name)

    def open(self):
        log.info(f"Opening '{self._name}' interface ... ")
        if self.is_open():
            log.info(f"'{self._name}' interface is already open!")
            return
        timeout = 3
        self._interface.click_button(
            button_name="X",
            button_area=self.MAIN_MENU_CROSS_AREA,
            button_images=self.MAIN_MENU_CROSS_IMAGES,
            is_open_func=self.is_open,
            is_opening=True,
            action_timeout=timeout
        )
        if self.is_open():
            log.info(f"Successfully opened '{self._name}' interface!")
            return
        raise RecoverableException(
            f"Failed to open '{self._name}' interface."
            f"Timeout: {timeout} seconds."
        )
    
    def close(self):
        log.info(f"Closing '{self._name}' interface ... ")
        if not self.is_open():
            log.info(f"'{self._name}' interface is already closed!")
            return
        timeout = 3
        self._interface.click_button(
            button_name="Cancel",
            button_area=ScreenCapture.GAME_WINDOW_AREA,
            button_images=self.CANCEL_BUTTON_IMAGES,
            is_open_func=self.is_open,
            is_opening=False,
            action_timeout=timeout
        )
        if not self.is_open():
            log.info(f"Successfully closed '{self._name}' interface!")
            return
        raise RecoverableException(
            f"Failed to close '{self._name}' interface. "
            f"Timeout: {timeout} seconds."
        )

    def click_logout(self):
        return self._interface.click_button(
            button_name="Logout", 
            button_area=ScreenCapture.GAME_WINDOW_AREA, 
            button_images=self.LOGOUT_BUTTON_IMAGES, 
            is_open_func=self.is_open,
            is_opening=False
        )

    def get_cross_button_pos(self):
        """X icon at the top right corner."""
        return self._interface._get_button_pos(
            search_area=self.MAIN_MENU_CROSS_AREA,
            images=self.MAIN_MENU_CROSS_IMAGES
        )

    @classmethod
    def is_open(cls):
        return len(
            ImageDetection.find_images(
                haystack=ScreenCapture.game_window(),
                needles=cls.MAIN_MENU_TITLE_IMAGES,
                confidence=0.95,
                method=TM_CCOEFF_NORMED
            )
        ) > 0

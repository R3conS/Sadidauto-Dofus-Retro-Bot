from src.logger import get_logger

log = get_logger()

from cv2 import TM_CCOEFF_NORMED

from src.bot._exceptions import RecoverableException
from src.bot._interfaces._interface import Interface
from src.utilities.general import load_image
from src.utilities.image_detection import ImageDetection
from src.utilities.screen_capture import ScreenCapture


class Caution:
    """Confirmation window that appears when clicking logout on Main Menu."""

    IMAGE_DIR_PATH = "src\\bot\\_interfaces\\_caution\\_images"
    YES_BUTTON_IMAGES = [
        load_image(IMAGE_DIR_PATH, "yes_button_950x785.png"),
        load_image(IMAGE_DIR_PATH, "yes_button_1000x785.png")
    ]
    NO_BUTTON_IMAGES = [
        load_image(IMAGE_DIR_PATH, "no_button_950x785.png"),
        load_image(IMAGE_DIR_PATH, "no_button_1000x785.png")
    ]
    CAUTION_TITLE_IMAGES = [
        load_image(IMAGE_DIR_PATH, "caution_title_950x785.png"),
        load_image(IMAGE_DIR_PATH, "caution_title_1000x785.png")
    ]

    def __init__(self):
        self._name = "Caution"
        self._interface = Interface(self._name)

    def close(self):
        log.info(f"Closing '{self._name}' interface ... ")
        if not self.is_open():
            log.info(f"'{self._name}' interface is already closed!")
            return
        self.click_no()
        if not self.is_open():
            log.info(f"Successfully closed '{self._name}' interface!")
            return
        raise RecoverableException(f"Failed to close '{self._name}' interface.")

    def click_yes(self):
        return self._interface.click_button(
            button_name="Yes",
            button_area=ScreenCapture.GAME_WINDOW_AREA,
            button_images=self.YES_BUTTON_IMAGES,
            is_open_func=self.is_open,
            is_opening=False
        )

    def click_no(self):
        return self._interface.click_button(
            button_name="No",
            button_area=ScreenCapture.GAME_WINDOW_AREA,
            button_images=self.NO_BUTTON_IMAGES,
            is_open_func=self.is_open,
            is_opening=False
        )

    @classmethod
    def is_open(cls):
        return len(
            ImageDetection.find_images(
                haystack=ScreenCapture.game_window(),
                needles=cls.CAUTION_TITLE_IMAGES,
                confidence=0.95,
                method=TM_CCOEFF_NORMED
            )
        ) > 0

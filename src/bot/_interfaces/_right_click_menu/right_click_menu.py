from src.logger import Logger
log = Logger.get_logger(Logger.DEBUG, True, True)

import cv2

from src.bot._interfaces._interface import Interface
from src.utilities.general import load_image
from src.utilities.image_detection import ImageDetection
from src.utilities.screen_capture import ScreenCapture


class RightClickMenu:
    """Options that appear when game area is right clicked."""

    IMAGE_DIR_PATH = "src\\bot\\_interfaces\\_right_click_menu\\_images"
    FLASH_QUALITY_IMAGE = load_image(IMAGE_DIR_PATH, "flash_quality.png")

    def __init__(self):
        self._name = "Right Click Menu"
        self._interface = Interface(self._name)

    def close(self):
        return self._interface.close(929, 51, self.is_open)

    @classmethod
    def is_open(cls):
        return len(
            ImageDetection.find_image(
                haystack=ScreenCapture.game_window(),
                needle=cls.FLASH_QUALITY_IMAGE,
                method=cv2.TM_SQDIFF_NORMED,
                confidence=0.995
            )
        ) > 0

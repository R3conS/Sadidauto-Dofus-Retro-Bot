from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import cv2

from ._interface import Interface
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture
from src.utilities import load_image


class RightClickMenu:
    """Options that appear when game area is right clicked."""

    def __init__(self):
        self._name = "Right Click Menu"
        self._interface = Interface(self._name)
        self._flash_quality_image = load_image("src\\bot\\_interfaces\\_images", "rcm_flash_quality.png")

    def close(self):
        return self._interface.close(929, 51, self.is_open)

    def is_open(self):
        return len(
            ImageDetection.find_image(
                haystack=ScreenCapture.game_window(),
                needle=self._flash_quality_image,
                method=cv2.TM_SQDIFF_NORMED,
                confidence=0.995
            )
        ) > 0

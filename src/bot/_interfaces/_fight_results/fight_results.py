from src.logger import get_logger

log = get_logger()

import cv2

from src.bot._interfaces._interface import Interface
from src.utilities.general import load_image
from src.utilities.image_detection import ImageDetection
from src.utilities.screen_capture import ScreenCapture


class FightResults:
    """Appears after combat has ended."""

    IMAGE_FOLDER_PATH = "src\\bot\\_interfaces\\_fight_results\\_images"
    CLOSE_BUTTON_IMAGES = [
        load_image(IMAGE_FOLDER_PATH, "close_button.png"),
        load_image(IMAGE_FOLDER_PATH, "close_button_2.png"),
    ]

    def __init__(self):
        self._name = "Fight Results"
        self._interface = Interface(self._name)

    def close(self):
        pos = self._get_close_button_pos()
        if pos is None:
            log.info(f"'{self._name}' interface is already closed!")
            return
        return self._interface.close(pos[0], pos[1], self.is_open)
        
    @classmethod
    def is_open(cls):
        return len(
            ImageDetection.find_images(
                haystack=ScreenCapture.game_window(),
                needles=cls.CLOSE_BUTTON_IMAGES,
                confidence=0.98,
                method=cv2.TM_SQDIFF_NORMED,
            )
        ) > 0

    @classmethod
    def _get_close_button_pos(cls):
        rectangle = ImageDetection.find_images(
            haystack=ScreenCapture.game_window(),
            needles=cls.CLOSE_BUTTON_IMAGES,
            confidence=0.98,
            method=cv2.TM_SQDIFF_NORMED,
        )
        if len(rectangle) <= 0:
            return None
        return ImageDetection.get_rectangle_center_point(rectangle[0])

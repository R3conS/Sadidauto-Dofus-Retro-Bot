from src.logger import get_logger

log = get_logger()

import cv2
from pyautogui import pixelMatchesColor

from src.bot._interfaces._interface import Interface
from src.utilities.general import load_image
from src.utilities.image_detection import ImageDetection
from src.utilities.screen_capture import ScreenCapture


class OfferOrInvite:
    """Exchange, challenge offers & guild, group invites."""

    IMAGE_FOLDER_PATH = "src\\bot\\_interfaces\\_offer_or_invite\\_images"
    IGNORE_BUTTON_IMAGES = [
        load_image(IMAGE_FOLDER_PATH, "ignore_official.png"),
        load_image(IMAGE_FOLDER_PATH, "ignore_abrak.png")
    ]

    def __init__(self):
        self._name = "Offer or Invite"
        self._interface = Interface(self._name)

    def close(self):
        pos = self._get_ignore_button_pos()
        if pos is None:
            log.info(f"'{self._name}' interface is already closed!")
            return
        return self._interface.close(pos[0], pos[1], self.is_open)

    @staticmethod
    def is_open():
        if all((
            pixelMatchesColor(406, 255, (81, 74, 60)),
            pixelMatchesColor(530, 255, (81, 74, 60)),
            pixelMatchesColor(284, 354, (213, 207, 170)),
            pixelMatchesColor(655, 354, (213, 207, 170)),
        )):
            if all((
                pixelMatchesColor(427, 350, (216, 99, 28)),
                pixelMatchesColor(513, 350, (216, 99, 28))
            )) or all((
                pixelMatchesColor(427, 350, (255, 97, 0)),
                pixelMatchesColor(513, 350, (255, 97, 0))
            )):
                return True
        return False

    @classmethod
    def _get_ignore_button_pos(cls):
        rectangle = ImageDetection.find_images(
            haystack=ScreenCapture.game_window(),
            needles=cls.IGNORE_BUTTON_IMAGES,
            confidence=0.98,
            method=cv2.TM_SQDIFF_NORMED,
        )
        if len(rectangle) <= 0:
            return None
        return ImageDetection.get_rectangle_center_point(rectangle[0])


if __name__ == "__main__":
    print(OfferOrInvite.is_open())
    pos = OfferOrInvite._get_ignore_button_pos()
    if pos is not None:
        import pyautogui
        pyautogui.moveTo(pos[0], pos[1])

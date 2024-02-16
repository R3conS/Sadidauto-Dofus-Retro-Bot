from src.logger import get_logger

log = get_logger()

from cv2 import TM_CCOEFF_NORMED

from src.bot._interfaces._interface import Interface
from src.utilities.general import load_image
from src.utilities.image_detection import ImageDetection
from src.utilities.screen_capture import ScreenCapture


class LoginScreen:

    IMAGE_FOLDER_PATH = "src\\bot\\_interfaces\\_login_screen\\_images"
    IDENTIFIER_IMAGES = [
        load_image(IMAGE_FOLDER_PATH, "login_screen_950x785_darker.png"),
        load_image(IMAGE_FOLDER_PATH, "login_screen_950x785_lighter.png"),
        load_image(IMAGE_FOLDER_PATH, "login_screen_1000x785_darker.png"),
        load_image(IMAGE_FOLDER_PATH, "login_screen_1000x785_lighter.png")
    ]

    def __init__(self):
        self._name = "Login Screen"
        self._interface = Interface(self._name)

    @classmethod
    def is_open(cls):
        return len(
            ImageDetection.find_images(
                haystack=ScreenCapture.game_window(),
                needles=cls.IDENTIFIER_IMAGES,
                confidence=0.95,
                method=TM_CCOEFF_NORMED,
            )
        ) > 0

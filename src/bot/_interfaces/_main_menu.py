from src.logger import Logger
log = Logger.get_logger(Logger.DEBUG, True, True)

from cv2 import TM_CCOEFF_NORMED

from src.bot._exceptions import RecoverableException
from src.bot._interfaces._interface import Interface
from src.utilities.general import load_image_full_path
from src.utilities.image_detection import ImageDetection
from src.utilities.ocr.ocr import OCR
from src.utilities.screen_capture import ScreenCapture


class MainMenu:
    """Appears when ESC is pressed or when X icon is clicked at the top right corner."""

    MAIN_MENU_CROSS_IMAGES = [
        load_image_full_path("src\\bot\\_interfaces\\_images\\main_menu_cross.png"),
        load_image_full_path("src\\bot\\_interfaces\\_images\\main_menu_cross_2.png"),
    ]

    def __init__(self):
        self._name = "Main Menu"
        self._interface = Interface(self._name)

    def open(self):
        return self._interface.open(*self._get_icon_pos(), self.is_open)
    
    def close(self):
        return self._interface.click_button((330, 243, 273, 188), "Cancel", self.is_open)

    def click_logout(self):
        return self._interface.click_button((330, 243, 273, 188), "Logout", self.is_open)

    @staticmethod
    def is_open():
        sc = ScreenCapture.custom_area((310, 194, 322, 57))
        sc = OCR.resize_image(sc, sc.shape[1] * 4, sc.shape[0] * 4)
        sc = OCR.convert_to_grayscale(sc)
        sc = OCR.binarize_image(sc, 205)
        sc = OCR.dilate_image(sc, 2)
        text = OCR.get_text_from_image(sc)
        return "Main" in text or "Menu" in text

    @classmethod
    def _get_icon_pos(cls):
        area = (850, 0, 140, 85)
        sc = ScreenCapture.custom_area(area)
        rectangles = ImageDetection.find_images(
            haystack=sc, 
            needles=cls.MAIN_MENU_CROSS_IMAGES, 
            confidence=0.9,
            method=TM_CCOEFF_NORMED
        )
        if len(rectangles) > 0:
            return ImageDetection.get_rectangle_center_point(
                (
                    rectangles[0][0] + area[0], 
                    rectangles[0][1] + area[1], 
                    rectangles[0][2], 
                    rectangles[0][3]
                )
            )
        raise RecoverableException("Failed to find the 'Main Menu' interface icon.")

from src.logger import Logger
log = Logger.get_logger(Logger.DEBUG, True, True)

from src.bot._interfaces._interface import Interface
from src.utilities.ocr.ocr import OCR
from src.utilities.screen_capture import ScreenCapture


class Caution:
    """Confirmation window that appears when clicking logout on Main Menu."""

    def __init__(self):
        self._name = "Caution"
        self._interface = Interface(self._name)

    def click_yes(self):
        return self._interface.click_button((274, 343, 436, 49), "Yes", self.is_open)

    def click_no(self):
        return self._interface.click_button((274, 343, 436, 49), "No", self.is_open)

    @staticmethod
    def is_open():
        sc = ScreenCapture.custom_area((219, 230, 529, 254))
        sc = OCR.resize_image(sc, sc.shape[1] * 4, sc.shape[0] * 4)
        sc = OCR.convert_to_grayscale(sc)
        sc = OCR.binarize_image(sc, 240)
        return "Caution" in OCR.get_text_from_image(sc).strip()

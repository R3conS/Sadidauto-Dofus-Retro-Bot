from src.logger import Logger
log = Logger.get_logger(Logger.DEBUG, True, True)

from src.bot._interfaces._interface import Interface
from src.utilities.ocr.ocr import OCR
from src.utilities.screen_capture import ScreenCapture


class Connection:
    """Connection lost popup that appears when account is disconnected."""

    def __init__(self):
        self._name = "Connection"
        self._interface = Interface(self._name)

    def click_yes(self):
        return self._interface.click_button((263, 432, 406, 44), "Yes", self.is_open)
   
    def click_no(self):
        return self._interface.click_button((468, 430, 203, 45), "No", self.is_open)

    @staticmethod
    def is_open():
        return "connection" in OCR.get_text_from_image(
            ScreenCapture.custom_area((223, 283, 546, 247))
        ).lower()


if __name__ == "__main__":
    print(Connection.is_open())

from src.logger import Logger
log = Logger.get_logger(Logger.DEBUG, True, True)

from time import perf_counter

from pyautogui import click, moveTo

from src.bot._exceptions import RecoverableException, UnrecoverableException
from src.bot._interfaces._interface import Interface
from src.utilities.image_detection import ImageDetection
from src.utilities.ocr.ocr import OCR
from src.utilities.screen_capture import ScreenCapture


class Connection:
    """Connection lost popup that appears when account is disconnected."""

    def __init__(self):
        self._name = "Connection"
        self._interface = Interface(self._name)

    def close(self):
        return self._interface.close(562, 453, self.is_open)

    @staticmethod
    def is_open():
        return "connection" in OCR.get_text_from_image(
            ScreenCapture.custom_area((223, 283, 546, 247))
        ).lower()

    @classmethod
    def click_yes(cls):
        yes_search_area = (313, 434, 140, 34)
        sc = ScreenCapture.custom_area(yes_search_area)
        scale = 2
        sc = OCR.resize_image(sc, sc.shape[1] * scale, sc.shape[0] * scale)
        sc = OCR.convert_to_grayscale(sc)
        sc = OCR.invert_image(sc)
        sc = OCR.binarize_image(sc, 70)
        result = OCR.get_text_from_image(sc, with_rectangles=True)

        if any(word == "Yes" for word, _ in result):
            for word, rectangle in result:
                if word == "Yes":
                    rectangle = tuple(int(x / scale) for x in rectangle)
                    rectangle = (
                        rectangle[0] + yes_search_area[0], 
                        rectangle[1] + yes_search_area[1], 
                        rectangle[2], 
                        rectangle[3]
                    )
                    x, y = ImageDetection.get_rectangle_center_point(rectangle)
                    
                    log.info("Clicking the 'Yes' button ... ")
                    moveTo(x, y)
                    click()
                    timeout = 5
                    start_time = perf_counter()
                    while perf_counter() - start_time <= timeout:
                        if not cls.is_open():
                            log.info("Successfully clicked the 'Yes' button!")
                            return
                    raise RecoverableException(
                        "Timed out while detecting if 'Yes' button was clicked successfully. "
                        f"Timeout: {timeout} seconds."
                    )

        raise UnrecoverableException("Failed to find the 'Yes' button.")


if __name__ == "__main__":
    print(Connection.is_open())

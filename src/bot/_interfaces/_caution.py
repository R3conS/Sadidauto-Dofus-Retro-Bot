from src.logger import Logger
log = Logger.get_logger(Logger.DEBUG, True, True)

from pyautogui import pixelMatchesColor

from src.bot._interfaces._interface import Interface


class Caution:
    """Confirmation window tha appears when clicking logout on Main Menu."""

    def __init__(self):
        self._name = "Caution"
        self._interface = Interface(self._name)

    @staticmethod
    def is_open():
        return all((
            pixelMatchesColor(280, 297, (213, 207, 170)),
            pixelMatchesColor(654, 303, (213, 207, 170)),
            pixelMatchesColor(426, 369, (255, 97, 0)),
            pixelMatchesColor(518, 369, (255, 97, 0)),
            pixelMatchesColor(465, 269, (81, 74, 60))
        ))

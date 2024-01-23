from src.logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from pyautogui import pixelMatchesColor

from ._interface import Interface


class Information:
    """Appears after a level up."""

    def __init__(self):
        self._name = "Information"
        self._interface = Interface(self._name)

    def close(self):
        return self._interface.close(480, 377, self.is_open)
        
    @staticmethod
    def is_open():
        return all((
            pixelMatchesColor(463, 261, (81, 74, 60)),
            pixelMatchesColor(302, 377, (213, 207, 170)),
            pixelMatchesColor(503, 376, (255, 97, 0))
        ))

from src.logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from pyautogui import pixelMatchesColor

from src.bot._interfaces._interface import Interface


class MainMenu:
    """Appears when ESC is pressed or when X icon is clicked at the top right corner."""

    def __init__(self):
        self._name = "Main Menu"
        self._interface = Interface(self._name)

    def open(self):
        return self._interface.open(920, 63, self.is_open)
    
    def close(self):
        return self._interface.close(468, 407, self.is_open)

    @staticmethod
    def is_open():
        return all((
            pixelMatchesColor(461, 230, (81, 74, 60)),
            pixelMatchesColor(540, 230, (81, 74, 60)),
            pixelMatchesColor(343, 257, (213, 207, 170)),
            pixelMatchesColor(589, 421, (213, 207, 170)),
            pixelMatchesColor(369, 278, (255, 97, 0))
        ))

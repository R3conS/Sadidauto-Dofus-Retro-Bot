from src.logger import Logger
log = Logger.get_logger()

from pyautogui import pixelMatchesColor

from src.bot._interfaces._interface import Interface


class Inventory:

    def __init__(self):
        self._name = "Inventory"
        self._interface = Interface(self._name)

    def open(self):
        return self._interface.open(690, 622, self.is_open)

    def close(self):
        return self._interface.close(690, 622, self.is_open)

    @staticmethod
    def is_open():
        return all((
            pixelMatchesColor(276, 311, (150, 138, 111)),
            pixelMatchesColor(905, 116, (213, 207, 170)),
            pixelMatchesColor(327, 255, (81, 74, 60))
        ))

from src.logger import Logger
log = Logger.get_logger(Logger.DEBUG, True, True)

from pyautogui import pixelMatchesColor

from src.bot._interfaces._interface import Interface


class Characteristics:

    def __init__(self):
        self._name = "Characteristics"
        self._interface = Interface(self._name)

    def open(self):
        return self._interface.open(613, 622, self.is_open)
        
    def close(self):
        return self._interface.close(613, 622, self.is_open)

    @staticmethod
    def is_open():
        return all((
            pixelMatchesColor(902, 117, (81, 74, 60)),
            pixelMatchesColor(870, 331, (81, 74, 60))
        ))

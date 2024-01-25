from src.logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter

from pyautogui import pixelMatchesColor, moveTo, click

from src.bot._interfaces._interface import Interface
from src.bot._exceptions import RecoverableException


class Connection:
    """Connection lost popup that appears when account is disconnected."""

    def __init__(self):
        self._name = "Connection"
        self._interface = Interface(self._name)

    def close(self):
        return self._interface.close(562, 453, self.is_open)

    @staticmethod
    def is_open():
        return all((
            pixelMatchesColor(257, 353, (213, 207, 170)),
            pixelMatchesColor(262, 472, (213, 207, 170)),
            pixelMatchesColor(466, 335, (81, 74, 60)),
            pixelMatchesColor(661, 335, (81, 74, 60)),
            pixelMatchesColor(437, 452, (255, 97, 0)),
            pixelMatchesColor(614, 451, (255, 97, 0))
        ))

    @classmethod
    def click_yes(cls):
        log.info(f"Clicking 'Yes' button ... ")
        moveTo(382, 452)
        click()
        
        timeout = 5
        start_time = perf_counter()
        while perf_counter() - start_time <= timeout:
            if not cls.is_open():
                log.info(f"Successfully clicked 'Yes' button!")
                return
        raise RecoverableException(
            "Timed out while detecting if 'Yes' button was clicked successfully. "
            f"Timeout: {timeout} seconds."
        )

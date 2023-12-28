from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter

from pyautogui import moveTo, click

from ._exceptions import Exceptions


class Interface:

    def __init__(self, name):
        self.name = name
        self._action_timeout = 3

    def open(self, x, y, is_open_func: callable):
        log.info(f"Opening '{self.name}' interface ... ")
        if is_open_func():
            log.info(f"'{self.name}' interface is already open!")
            return
        moveTo(x, y)
        click()
        start_time = perf_counter()
        while perf_counter() - start_time <= self._action_timeout:
            if is_open_func():
                log.info(f"Successfully opened '{self.name}' interface!")
                return
        raise Exceptions.FailedToOpenInterface(f"Timed out while opening '{self.name}' interface.")

    def close(self, x, y, is_open_func: callable):
        log.info(f"Closing '{self.name}' interface ... ")
        if not is_open_func():
            log.info(f"'{self.name}' interface is already closed!")
            return
        moveTo(x, y)
        click()
        start_time = perf_counter()
        while perf_counter() - start_time <= self._action_timeout:
            if not is_open_func():
                log.info(f"Successfully closed '{self.name}' interface!")
                return
        raise Exceptions.FailedToCloseInterface(f"Timed out while closing '{self.name}' interface.")

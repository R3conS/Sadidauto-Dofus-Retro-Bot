from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter

from pyautogui import moveTo, click

from ._exceptions import Exceptions


class Interface:

    def __init__(self, name):
        self._name = name
        self._action_timeout = 3

    def open(self, x, y, is_open_func: callable):
        log.info(f"Opening '{self._name}' interface ... ")
        if is_open_func():
            log.info(f"'{self._name}' interface is already open!")
            return
        moveTo(x, y)
        click()
        start_time = perf_counter()
        while perf_counter() - start_time <= self._action_timeout:
            if is_open_func():
                log.info(f"Successfully opened '{self._name}' interface!")
                return
        raise Exceptions.FailedToOpenInterface(f"Timed out while opening '{self._name}' interface.")

    def close(self, x, y, is_open_func: callable):
        log.info(f"Closing '{self._name}' interface ... ")
        if not is_open_func():
            log.info(f"'{self._name}' interface is already closed!")
            return
        moveTo(x, y)
        click()
        start_time = perf_counter()
        while perf_counter() - start_time <= self._action_timeout:
            if not is_open_func():
                log.info(f"Successfully closed '{self._name}' interface!")
                return
        raise Exceptions.FailedToCloseInterface(f"Timed out while closing '{self._name}' interface.")

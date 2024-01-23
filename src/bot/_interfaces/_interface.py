from src.logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter

from pyautogui import moveTo, click

from src.bot._exceptions import RecoverableException


class Interface:

    def __init__(self, name):
        self._name = name
        self._action_timeout = 5

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
        raise RecoverableException(f"Failed to open '{self._name}' interface.")

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
        raise RecoverableException(f"Failed to close '{self._name}' interface.")

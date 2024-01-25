from src.logger import Logger
log = Logger.get_logger(Logger.DEBUG, True, True)

from time import perf_counter

import pyautogui as pyag

from src.bot._exceptions import RecoverableException


class TurnBar:
    
    NAME = "Turn Bar"

    @classmethod
    def is_shrunk(cls):
        """All locations are along the left edge of the first card in the turn bar."""
        return not any((
            pyag.pixelMatchesColor(869, 548, (255, 255, 255)),
            pyag.pixelMatchesColor(869, 554, (255, 255, 255)),
            pyag.pixelMatchesColor(869, 565, (255, 255, 255)),
            pyag.pixelMatchesColor(869, 573, (255, 255, 255)),
            pyag.pixelMatchesColor(869, 579, (255, 255, 255)),
            pyag.pixelMatchesColor(869, 585, (255, 255, 255))
        ))

    @classmethod
    def shrink(cls):
        log.info(f"Shrinking '{cls.NAME}' ...")

        if cls.is_shrunk():
            log.info(f"'{cls.NAME}' is already shrunk.")
            return

        pyag.moveTo(924, 567)
        pyag.click()

        # Checking within a timer to give shrinking animation time to finish.
        timeout = 3
        start_time = perf_counter()
        while perf_counter() - start_time <= timeout:
            if cls.is_shrunk():
                log.info(f"Successfully shrunk '{cls.NAME}'.")
                return
            
        raise RecoverableException(
            f"Timed out while detecting whether '{cls.NAME}' has been successfully shrunk. "
            f"Timeout: {timeout} seconds."
        )

    @classmethod
    def unshrink(cls):
        log.info(f"Unshrinking '{cls.NAME}' ...")

        if not cls.is_shrunk():
            log.info(f"'{cls.NAME}' is already unshrunk.")
            return

        pyag.moveTo(924, 567)
        pyag.click()

        # Checking within a timer to give shrinking animation time to finish.
        timeout = 3
        start_time = perf_counter()
        while perf_counter() - start_time <= timeout:
            if not cls.is_shrunk():
                log.info(f"Successfully unshrunk '{cls.NAME}'.")
                return 

        raise RecoverableException(
            f"Timed out while detecting whether '{cls.NAME}' has been successfully unshrunk. "
            f"Timeout: {timeout} seconds."
        )

from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter

import pyautogui as pyag

from src.bot.states.in_combat.status_enum import Status


class TurnBar:
    
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
        pyag.moveTo(924, 567)
        pyag.click()

        # Checking within a timer to give shrinking animation time to finish.
        start_time = perf_counter()
        while perf_counter() - start_time <= 3:
            if cls.is_shrunk():
                log.info("Successfully shrunk turn bar.")
                return Status.SUCCESSFULLY_SHRUNK_TURN_BAR
        log.error("Timed out while shrinking turn bar.")
        return Status.TIMED_OUT_WHILE_SHRINKING_TURN_BAR

    @classmethod
    def unshrink(cls):
        pyag.moveTo(924, 567)
        pyag.click()

        # Checking within a timer to give shrinking animation time to finish.
        start_time = perf_counter()
        while perf_counter() - start_time <= 3:
            if not cls.is_shrunk():
                log.info("Successfully unshrunk turn bar.")
                return Status.SUCCESSFULLY_UNSHRUNK_TURN_BAR
        log.error("Timed out while unshrinking turn bar.")
        return Status.TIMED_OUT_WHILE_UNSHRINKING_TURN_BAR

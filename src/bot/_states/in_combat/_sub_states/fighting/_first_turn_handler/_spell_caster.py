from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from .._spells.spells import Spells
from src.bot._states.in_combat._status_enum import Status
from src.bot._exceptions import RecoverableException


class Caster:

    @staticmethod
    def cast_spells(cast_coords: tuple[int, int]):
        log.info("Casting spells ...")
        while True:
            if Spells.EARTHQUAKE.is_available():
                result = Spells.EARTHQUAKE.cast(cast_coords[0], cast_coords[1])
                if result != Status.SUCCESSFULLY_CAST_SPELL:
                    raise RecoverableException("First turn spell casting failed.")
            elif Spells.POISONED_WIND.is_available():
                result = Spells.POISONED_WIND.cast(cast_coords[0], cast_coords[1])
                if result != Status.SUCCESSFULLY_CAST_SPELL:
                    raise RecoverableException("First turn spell casting failed.")
            elif Spells.SYLVAN_POWER.is_available():
                result = Spells.SYLVAN_POWER.cast(cast_coords[0], cast_coords[1])
                if result != Status.SUCCESSFULLY_CAST_SPELL:
                    raise RecoverableException("First turn spell casting failed.")
            if (
                not Spells.EARTHQUAKE.is_available()
                and not Spells.POISONED_WIND.is_available()
                and not Spells.SYLVAN_POWER.is_available()
            ):
                log.info("Finished casting spells.")
                break

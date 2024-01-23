from src.logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from .._spells.spells import Spells
from .._spells._exceptions import FailedToCastSpell
from src.bot._exceptions import RecoverableException


class Caster:

    @staticmethod
    def cast_spells(cast_coords: tuple[int, int]):
        log.info("Casting spells during the first turn ...")
        try:
            while True:
                if Spells.EARTHQUAKE.is_available():
                    Spells.EARTHQUAKE.cast(cast_coords[0], cast_coords[1])
                elif Spells.POISONED_WIND.is_available():
                    Spells.POISONED_WIND.cast(cast_coords[0], cast_coords[1])
                elif Spells.SYLVAN_POWER.is_available():
                    Spells.SYLVAN_POWER.cast(cast_coords[0], cast_coords[1])
                else:
                    log.info("Finished casting first turn spells.")
                    break
        except FailedToCastSpell:
            raise RecoverableException("Failed to finish casting spells during the first turn.")

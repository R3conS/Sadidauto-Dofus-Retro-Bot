from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from .._spells.spells import Spells
from src.bot._states.in_combat._status_enum import Status


class Caster:

    @staticmethod
    def cast_spells(cast_coords: tuple[int, int]):
        log.info("Casting spells ...")
        while True:
            if Spells.EARTHQUAKE.is_available():
                result = Spells.EARTHQUAKE.cast(cast_coords[0], cast_coords[1])
                if result != Status.SUCCESSFULLY_CAST_SPELL:
                    return Status.FAILED_TO_CAST_SPELL
            elif Spells.POISONED_WIND.is_available():
                result = Spells.POISONED_WIND.cast(cast_coords[0], cast_coords[1])
                if result != Status.SUCCESSFULLY_CAST_SPELL:
                    return Status.FAILED_TO_CAST_SPELL
            elif Spells.SYLVAN_POWER.is_available():
                result = Spells.SYLVAN_POWER.cast(cast_coords[0], cast_coords[1])
                if result != Status.SUCCESSFULLY_CAST_SPELL:
                    return Status.FAILED_TO_CAST_SPELL
            if (
                not Spells.EARTHQUAKE.is_available()
                and not Spells.POISONED_WIND.is_available()
                and not Spells.SYLVAN_POWER.is_available()
            ):
                log.info("Finished casting spells.")
                return Status.SUCCESSFULLY_FINISHED_FIRST_TURN_SPELL_CASTING

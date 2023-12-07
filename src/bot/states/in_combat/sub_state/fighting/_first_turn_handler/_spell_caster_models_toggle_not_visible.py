from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from .._spells import Spells
from ..status_enum import Status


class Caster:

    @staticmethod
    def cast_spells(character_pos: tuple[int, int]):
        log.info("Casting spells.")
        while True:
            if Spells.is_earthquake_available():
                result = Spells.cast_earthquake(character_pos[0], character_pos[1])
                if result != Status.SUCCESSFULLY_CAST_SPELL:
                    return Status.FAILED_TO_CAST_SPELL
            elif Spells.is_poisoned_wind_available():
                result = Spells.cast_poisoned_wind(character_pos[0], character_pos[1])
                if result != Status.SUCCESSFULLY_CAST_SPELL:
                    return Status.FAILED_TO_CAST_SPELL
            elif Spells.is_sylvan_power_available():
                result = Spells.cast_sylvan_power(character_pos[0], character_pos[1])
                if result != Status.SUCCESSFULLY_CAST_SPELL:
                    return Status.FAILED_TO_CAST_SPELL
            if (
                not Spells.is_earthquake_available()
                and not Spells.is_poisoned_wind_available()
                and not Spells.is_sylvan_power_available()
            ):
                return Status.SUCCESSFULLY_FINISHED_FIRST_TURN_SPELL_CASTING

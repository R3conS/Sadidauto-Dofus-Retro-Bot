from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from src.bot.map_changer.map_changer import MapChanger
from ._starting_cell_and_side_getter import Getter as StartingCellAndSideGetter
from ..data.getter import Getter as FightingDataGetter
from .._spells import Spells
from ..status_enum import Status


class Caster:

    def __init__(self, char_turn_card_pos):
        self.char_turn_card_pos = char_turn_card_pos

    def cast_spells(self):
        log.info("Casting spells.")
        while True:
            if Spells.is_earthquake_available():
                result = Spells.cast_earthquake(self.char_turn_card_pos[0], self.char_turn_card_pos[1])
                if result != Status.SUCCESSFULLY_CAST_SPELL:
                    return Status.FAILED_TO_CAST_SPELL
            elif Spells.is_poisoned_wind_available():
                result = Spells.cast_poisoned_wind(self.char_turn_card_pos[0], self.char_turn_card_pos[1])
                if result != Status.SUCCESSFULLY_CAST_SPELL:
                    return Status.FAILED_TO_CAST_SPELL
            elif Spells.is_sylvan_power_available():
                result = Spells.cast_sylvan_power(self.char_turn_card_pos[0], self.char_turn_card_pos[1])
                if result != Status.SUCCESSFULLY_CAST_SPELL:
                    return Status.FAILED_TO_CAST_SPELL
            if (
                not Spells.is_earthquake_available()
                and not Spells.is_poisoned_wind_available()
                and not Spells.is_sylvan_power_available()
            ):
                return Status.SUCCESSFULLY_FINISHED_FIRST_TURN_SPELL_CASTING

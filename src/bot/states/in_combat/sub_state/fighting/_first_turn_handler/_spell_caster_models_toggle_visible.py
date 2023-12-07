from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from src.bot.map_changer.map_changer import MapChanger
from ._starting_cell_and_side_getter import Getter as StartingCellAndSideGetter
from ..data.getter import Getter as FightingDataGetter
from .._spells import Spells
from ..status_enum import Status


class Caster:

    def __init__(self, script, initial_character_pos):
        self.__spell_casting_data = FightingDataGetter.get_data_object(script).get_spell_casting_data()
        self.__starting_cell_coords = StartingCellAndSideGetter(script).get_starting_cell_coords(initial_character_pos)
        self.__starting_side_color = StartingCellAndSideGetter(script).get_starting_side_color(initial_character_pos)

    def cast_spells(self):
        log.info("Casting spells.")
        while True:
            if Spells.is_earthquake_available():
                cast_coords = self.get_spell_cast_coords("earthquake")
                result = Spells.cast_earthquake(cast_coords[0], cast_coords[1])
                if result != Status.SUCCESSFULLY_CAST_SPELL:
                    return Status.FAILED_TO_CAST_SPELL
            elif Spells.is_poisoned_wind_available():
                cast_coords = self.get_spell_cast_coords("poisoned_wind")
                result = Spells.cast_poisoned_wind(cast_coords[0], cast_coords[1])
                if result != Status.SUCCESSFULLY_CAST_SPELL:
                    return Status.FAILED_TO_CAST_SPELL
            elif Spells.is_sylvan_power_available():
                cast_coords = self.get_spell_cast_coords("sylvan_power")
                result = Spells.cast_sylvan_power(cast_coords[0], cast_coords[1])
                if result != Status.SUCCESSFULLY_CAST_SPELL:
                    return Status.FAILED_TO_CAST_SPELL
            if (
                not Spells.is_earthquake_available()
                and not Spells.is_poisoned_wind_available()
                and not Spells.is_sylvan_power_available()
            ):
                return Status.SUCCESSFULLY_FINISHED_FIRST_TURN_SPELL_CASTING
                
    def get_spell_cast_coords(self, spell: str):
        current_map_coords = MapChanger.get_current_map_coords()
        for map_coords, map_data in self.__spell_casting_data.items():
            if map_coords == current_map_coords:
                for side_color, side_data in map_data.items():
                    if side_color == self.__starting_side_color:
                        for spell_name, spell_cast_data in side_data.items():
                            if spell_name == spell:
                                if isinstance(spell_cast_data, tuple):
                                    return spell_cast_data
                                try:
                                    return spell_cast_data[self.__starting_cell_coords]
                                except KeyError:
                                    raise Exception(
                                        f"No spell casting data for starting cell {self.__starting_cell_coords} "
                                        f"on starting side color '{self.__starting_side_color}' on map '{map_coords}'."
                                    )
        raise Exception(f"No spell casting data for spell '{spell}' on map '{current_map_coords}'.")

from .._character_finder import Finder as CharacterFinder
from ..status_enum import Status
from .._spells import Spells
from ._spell_caster import Caster as SpellCaster
from .._fight_preferences.turn_bar import TurnBar


class Handler:

    @classmethod
    def handle(cls, character_name: str):
        if not cls.is_any_spell_available():
            return Status.NO_SPELLS_AVAILABLE
        
        if TurnBar.is_shrunk():
            result = TurnBar.unshrink()
            if result == Status.TIMED_OUT_WHILE_UNSHRINKING_TURN_BAR:
                return Status.FAILED_TO_HANDLE_SUBSEQUENT_TURN_ACTIONS
            
        result = SpellCaster.cast_spells(character_name)
        # ToDo: continue implementing this.
            
    @staticmethod
    def is_any_spell_available():
        return (
            Spells.is_earthquake_available()
            or Spells.is_poisoned_wind_available()
            or Spells.is_sylvan_power_available()
            or Spells.is_bramble_available()
        )

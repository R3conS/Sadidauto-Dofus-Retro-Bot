from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from ..status_enum import Status
from .._spells import Spells
from ._spell_caster import Caster as SpellCaster
from .._fight_preferences.turn_bar import TurnBar


class Handler:

    @classmethod
    def handle(cls, character_name: str):
        log.info("Handling subsequent turn actions ...")

        if not cls.is_any_spell_available():
            return Status.NO_SPELLS_AVAILABLE
        
        if TurnBar.is_shrunk():
            result = TurnBar.unshrink()
            if result == Status.TIMED_OUT_WHILE_UNSHRINKING_TURN_BAR:
                return Status.FAILED_TO_HANDLE_SUBSEQUENT_TURN_ACTIONS
            
        result = SpellCaster.cast_spells(character_name)
        if (
            result == Status.FAILED_TO_CAST_CORE_SPELLS
            or result == Status.FAILED_TO_CAST_NON_CORE_SPELLS
        ):
            return Status.FAILED_TO_HANDLE_SUBSEQUENT_TURN_ACTIONS

        return Status.SUCCESSFULLY_HANDLED_SUBSEQUENT_TURN_ACTIONS
            
    @staticmethod
    def is_any_spell_available():
        return (
            Spells.is_earthquake_available()
            or Spells.is_poisoned_wind_available()
            or Spells.is_sylvan_power_available()
            or Spells.is_bramble_available()
        )

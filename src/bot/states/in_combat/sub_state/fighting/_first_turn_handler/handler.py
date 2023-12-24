from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from .._character_finder import Finder as CharacterFinder
from .._fight_preferences.models import Models
from .._fight_preferences.turn_bar import TurnBar
from ..status_enum import Status
from ._character_mover import Mover as CharacterMover
from ._spell_caster import Caster as SpellCaster


class Handler:

    @classmethod
    def handle(cls, script: str, character_name: str):
        log.info("Handling first turn actions ...")
        
        if not TurnBar.is_shrunk():
            log.info("Shrinking turn bar.")
            result = TurnBar.shrink()
            if result == Status.TIMED_OUT_WHILE_SHRINKING_TURN_BAR:
                return Status.FAILED_TO_HANDLE_FIRST_TURN_ACTIONS

        if Models.is_toggle_icon_visible(): # It's invisible after a reconnect.
            log.info("Models toggle icon is visible.")
            result = cls._handle_models_toggle_icon_visible(script, character_name)
            if (
                result == Status.FAILED_TO_DISABLE_MODELS
                or result == Status.FAILED_TO_GET_CHARACTER_POS_BY_CIRCLES
                or result == Status.FAILED_TO_MOVE_CHARACTER_DURING_FIRST_TURN
                or result == Status.FAILED_TO_CAST_SPELL
            ):
                return Status.FAILED_TO_HANDLE_FIRST_TURN_ACTIONS
        else:
            log.info("Models toggle icon is not visible.")
            result = cls._handle_models_toggle_icon_not_visible(character_name)
            if (
                result == Status.FAILED_TO_GET_CHARACTER_POS_BY_TURN_BAR
                or result == Status.FAILED_TO_CAST_SPELL
            ):
                return Status.FAILED_TO_HANDLE_FIRST_TURN_ACTIONS
            
        return Status.SUCCESSFULLY_HANDLED_FIRST_TURN_ACTIONS

    @classmethod
    def _handle_models_toggle_icon_visible(cls, script: str, character_name: str):
        if not Models.are_disabled():
            result = Models.disable()
            if (
                result == Status.FAILED_TO_GET_MODELS_TOGGLE_ICON_POS
                or result == Status.TIMED_OUT_WHILE_DISABLING_MODELS
            ):
                return Status.FAILED_TO_DISABLE_MODELS

        initial_character_pos = CharacterFinder.find_by_circles(character_name)
        if initial_character_pos == Status.TIMED_OUT_WHILE_WAITING_FOR_INFO_CARD_TO_APPEAR:
            return Status.FAILED_TO_GET_CHARACTER_POS_BY_CIRCLES
        
        char_mover = CharacterMover(script, initial_character_pos)
        result = char_mover.move()
        if (
            result == Status.TIMED_OUT_WHILE_DETECTING_IF_CHARACTER_MOVED
            or result == Status.FAILED_TO_DETECT_IF_DESTINATION_CELL_IS_HIGHIGHTED
        ):
            return Status.FAILED_TO_MOVE_CHARACTER_DURING_FIRST_TURN
        
        result = SpellCaster.cast_spells(char_mover.get_destination_cell_coords())
        if result == Status.FAILED_TO_CAST_SPELL:
            return result

        return Status.SUCCESSFULLY_HANDLED_FIRST_TURN_ACTIONS

    @classmethod
    def _handle_models_toggle_icon_not_visible(self, character_name: str):
        char_pos = CharacterFinder.find_by_turn_bar(character_name)
        if not isinstance(char_pos, tuple):
            return Status.FAILED_TO_GET_CHARACTER_POS_BY_TURN_BAR

        result = SpellCaster.cast_spells(char_pos)
        if result == Status.FAILED_TO_CAST_SPELL:
            return result
        
        return Status.SUCCESSFULLY_HANDLED_FIRST_TURN_ACTIONS

from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from .._character_finder import Finder as CharacterPosFinder
from .._fight_preferences.models import Models
from .._fight_preferences.turn_bar import TurnBar
from ..status_enum import Status
from ._character_mover import Mover as CharacterMover
from ._spell_caster_models_toggle_visible import Caster as SpellCasterModelsToggleVisible
from ._spell_caster_models_toggle_not_visible import Caster as SpellCasterModelsToggleNotVisible


class Handler:

    @classmethod
    def handle(cls, script: str, character_name: str):
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

        initial_character_pos = CharacterPosFinder.find_by_circles(character_name)
        if initial_character_pos == Status.TIMED_OUT_WHILE_WAITING_FOR_INFO_CARD_TO_APPEAR:
            return Status.FAILED_TO_GET_CHARACTER_POS_BY_CIRCLES
        
        result = CharacterMover(script, initial_character_pos).move()
        if (
            result == Status.TIMED_OUT_WHILE_DETECTING_IF_CHARACTER_MOVED
            or result == Status.FAILED_TO_DETECT_IF_DESTINATION_CELL_IS_HIGHIGHTED
        ):
            return Status.FAILED_TO_MOVE_CHARACTER_DURING_FIRST_TURN
        
        result = SpellCasterModelsToggleVisible(script, initial_character_pos).cast_spells()
        if result == Status.FAILED_TO_CAST_SPELL:
            return result
        
        return Status.SUCCESSFULLY_HANDLED_FIRST_TURN_ACTIONS

    @classmethod
    def _handle_models_toggle_icon_not_visible(self, character_name: str):
        char_turn_card_pos = CharacterPosFinder.find_by_turn_bar(character_name)
        if char_turn_card_pos == Status.TIMED_OUT_WHILE_WAITING_FOR_INFO_CARD_TO_APPEAR:
            return Status.FAILED_TO_GET_CHARACTER_POS_BY_TURN_BAR

        result = SpellCasterModelsToggleNotVisible(char_turn_card_pos).cast_spells()
        if result == Status.FAILED_TO_CAST_SPELL:
            return result
        
        return Status.SUCCESSFULLY_HANDLED_FIRST_TURN_ACTIONS

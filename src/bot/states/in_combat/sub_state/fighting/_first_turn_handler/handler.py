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

    def __init__(self, script: str, character_name: str):
        self.__script = script
        self.__character_pos_finder = CharacterPosFinder(character_name)

    def handle(self):
        if not TurnBar.is_shrunk():
            log.info("Shrinking turn bar.")
            result = TurnBar.shrink()
            if result == Status.TIMED_OUT_WHILE_SHRINKING_TURN_BAR:
                return Status.FAILED_TO_HANDLE_FIRST_TURN_ACTIONS_MODELS_TOGGLE_ICON_VISIBLE

        if Models.is_toggle_icon_visible(): # It's invisible after a reconnect.
            log.info("Models toggle icon is visible.")
            result = self._handle_models_toggle_icon_visible()
            if (
                result == Status.FAILED_TO_DISABLE_MODELS
                or result == Status.FAILED_TO_GET_CHARACTER_POS_BY_CIRCLES
                or result == Status.FAILED_TO_MOVE_CHARACTER_DURING_FIRST_TURN
                or result == Status.FAILED_TO_CAST_SPELL
            ):
                return Status.FAILED_TO_HANDLE_FIRST_TURN_ACTIONS_MODELS_TOGGLE_ICON_VISIBLE
        else:
            log.info("Models toggle icon is not visible.")
            result = self._handle_models_toggle_icon_not_visible()
            if (
                result == Status.FAILED_TO_GET_CHARACTER_POS_BY_TURN_BAR
                or result == Status.FAILED_TO_CAST_SPELL
            ):
                return Status.FAILED_FIRST_TURN_SPELL_CASTING_MODELS_TOGGLE_ICON_NOT_VISIBLE
            
        return Status.SUCCESSFULLY_HANDLED_FIRST_TURN_ACTIONS

    def _handle_models_toggle_icon_visible(self):
        if not Models.are_disabled():
            result = Models.disable()
            if (
                result == Status.FAILED_TO_GET_MODELS_TOGGLE_ICON_POS
                or result == Status.TIMED_OUT_WHILE_DISABLING_MODELS
            ):
                return Status.FAILED_TO_DISABLE_MODELS

        initial_character_pos = self.__character_pos_finder.find_by_circles()
        if initial_character_pos == Status.TIMED_OUT_WHILE_WAITING_FOR_INFO_CARD_TO_APPEAR:
            return Status.FAILED_TO_GET_CHARACTER_POS_BY_CIRCLES
        
        result = CharacterMover(self.__script, initial_character_pos).move()
        if (
            result == Status.TIMED_OUT_WHILE_DETECTING_IF_CHARACTER_MOVED
            or result == Status.FAILED_TO_DETECT_IF_DESTINATION_CELL_IS_HIGHIGHTED
        ):
            return Status.FAILED_TO_MOVE_CHARACTER_DURING_FIRST_TURN
        
        result = SpellCasterModelsToggleVisible(self.__script, initial_character_pos).cast_spells()
        if result == Status.FAILED_TO_CAST_SPELL:
            return result
        
        return Status.SUCCESSFULLY_HANDLED_FIRST_TURN_ACTIONS

    def _handle_models_toggle_icon_not_visible(self):
        char_turn_card_pos = self.__character_pos_finder.find_by_turn_bar()
        if char_turn_card_pos == Status.TIMED_OUT_WHILE_WAITING_FOR_INFO_CARD_TO_APPEAR:
            return Status.FAILED_TO_GET_CHARACTER_POS_BY_TURN_BAR

        result = SpellCasterModelsToggleNotVisible(char_turn_card_pos).cast_spells()
        if result == Status.FAILED_TO_CAST_SPELL:
            return result
        
        return Status.SUCCESSFULLY_HANDLED_FIRST_TURN_ACTIONS

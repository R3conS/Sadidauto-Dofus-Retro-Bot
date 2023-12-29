from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from ._character_mover import Mover as CharacterMover
from ._spell_caster import Caster as SpellCaster
from .._character_finder import Finder as CharacterFinder
from src.bot._states.in_combat._combat_options.models import Models
from src.bot._states.in_combat._combat_options.turn_bar import TurnBar
from src.bot._states.in_combat._status_enum import Status


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
                or result == Status.FAILED_TO_CAST_SPELL
            ):
                return Status.FAILED_TO_HANDLE_FIRST_TURN_ACTIONS
        else:
            log.error("Models toggle icon is not visible.")
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
        
        character_pos = CharacterFinder.find_by_circles(character_name)
        mover = CharacterMover(script, character_name, character_pos)

        result = mover.move()
        if (
            result == Status.SUCCESSFULLY_MOVED_CHARACTER
            or result == Status.CHARACTER_IS_ALREADY_ON_CORRECT_CELL
        ):
            cast_coords = mover._get_destination_cell_coords()
        elif (
            result == Status.CHARACTER_DID_NOT_START_FIRST_TURN_ON_VALID_CELL
            or result == Status.TIMED_OUT_WHILE_DETECTING_IF_CHARACTER_MOVED
            or result == Status.FAILED_TO_DETECT_IF_DESTINATION_CELL_IS_HIGHIGHTED
        ):
            cast_coords = character_pos
        
        if SpellCaster.cast_spells(cast_coords) == Status.FAILED_TO_CAST_SPELL:
            return Status.FAILED_TO_CAST_SPELL

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

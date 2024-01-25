from src.logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from src.bot._states.in_combat._combat_options.combat_options import CombatOptions
from src.bot._states.in_combat._sub_states.fighting._first_turn_handler._character_mover import Mover as CharacterMover
from src.bot._states.in_combat._sub_states.fighting._first_turn_handler._character_mover import FailedToMoveCharacter
from src.bot._states.in_combat._sub_states.fighting._first_turn_handler._spell_caster import Caster as SpellCaster
from src.bot._states.in_combat._sub_states.fighting._character_finder import Finder as CharacterFinder


class Handler:

    @classmethod
    def handle(cls, script: str, character_name: str):
        log.info("Handling first turn actions ...")
        if not CombatOptions.TACTICAL_MODE.is_on():
            CombatOptions.TACTICAL_MODE.turn_on()
        
        if not CombatOptions.TURN_BAR.is_shrunk():
            CombatOptions.TURN_BAR.shrink()

        if CombatOptions.MODELS.is_toggle_icon_visible(): # It's invisible after a reconnect.
            log.info("'Models' toggle icon is visible.")
            cls._handle_models_toggle_icon_visible(script, character_name)
        else:
            log.error("'Models' toggle icon is not visible.")
            cls._handle_models_toggle_icon_not_visible(character_name)
            
    @classmethod
    def _handle_models_toggle_icon_visible(cls, script: str, character_name: str):
        if not CombatOptions.MODELS.is_on():
            CombatOptions.MODELS.turn_on()
        
        character_pos = CharacterFinder.find_by_circles(character_name)
        character_mover = CharacterMover(script, character_name, character_pos)

        try:
            character_mover.move()
            cast_coords = character_mover._get_destination_cell_coords()
        except FailedToMoveCharacter:
            cast_coords = character_pos
        
        SpellCaster.cast_spells(cast_coords)

    @classmethod
    def _handle_models_toggle_icon_not_visible(self, character_name: str):
        SpellCaster.cast_spells(CharacterFinder.find_by_turn_bar(character_name))

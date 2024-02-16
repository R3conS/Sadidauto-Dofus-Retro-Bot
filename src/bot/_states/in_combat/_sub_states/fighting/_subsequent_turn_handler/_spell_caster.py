from src.logger import get_logger

log = get_logger()

import pyautogui as pyag

from src.bot._exceptions import RecoverableException
from src.bot._states.in_combat._sub_states.fighting._character_finder import Finder as CharacterFinder
from src.bot._states.in_combat._sub_states.fighting._character_finder import TimedOutWhileWaitingForInfoCard
from src.bot._states.in_combat._sub_states.fighting._spells._exceptions import FailedToCastSpell
from src.bot._states.in_combat._sub_states.fighting._spells.spells import Spells
from src.bot._states.in_combat._sub_states.fighting._turn_detector import TurnDetector
from src.utilities.general import move_mouse_off_game_area


class Caster:

    @classmethod
    def cast_spells(cls, character_name: str):
        log.info("Casting spells during a subsequent turn ...")
        if cls._is_any_core_spell_available():
            cls._handle_core_spells(character_name)
            
        if cls._is_any_non_core_spell_available():
            cls._handle_non_core_spells(character_name)

        log.info("Finished casting spells during a subsequent turn.")

    @staticmethod
    def is_any_spell_available():
        return (
            Spells.EARTHQUAKE.is_available()
            or Spells.POISONED_WIND.is_available()
            or Spells.SYLVAN_POWER.is_available()
            or Spells.BRAMBLE.is_available()
        )

    @staticmethod
    def _is_any_core_spell_available():
        return (
            Spells.EARTHQUAKE.is_available()
            or Spells.POISONED_WIND.is_available()
            or Spells.SYLVAN_POWER.is_available()
        )

    @staticmethod
    def _is_any_non_core_spell_available():
        return Spells.BRAMBLE.is_available()

    @staticmethod
    def _handle_core_spells(character_name: str):
        character_pos = CharacterFinder.find_by_turn_bar(character_name)
        try:
            while True:
                if Spells.EARTHQUAKE.is_available():
                    Spells.EARTHQUAKE.cast(character_pos[0], character_pos[1])
                elif Spells.POISONED_WIND.is_available():
                    Spells.POISONED_WIND.cast(character_pos[0], character_pos[1])
                elif Spells.SYLVAN_POWER.is_available():
                    Spells.SYLVAN_POWER.cast(character_pos[0], character_pos[1])
                else:
                    break
        except FailedToCastSpell:
            raise RecoverableException("Failed to finish casting core spells during a subsequent turn.")

    @classmethod
    def _handle_non_core_spells(cls, character_name: str):
        cls._handle_bramble(character_name)

    @classmethod
    def _handle_bramble(cls, character_name: str):
        while True:
            if not Spells.BRAMBLE.is_available():
                break

            monster_locations = cls._get_monster_locations(character_name)
            if monster_locations is None: # Fight ended.
                break
                
            for x, y in monster_locations:
                try:
                    Spells.BRAMBLE.cast(x, y)
                    move_mouse_off_game_area()
                    break
                except FailedToCastSpell:
                    continue
                
        move_mouse_off_game_area()

    @classmethod
    def _get_monster_locations(cls, character_name: str):
        monster_locations = []
        blue_circles = CharacterFinder.get_blue_circle_locations()
        for circle in blue_circles:
            pyag.moveTo(circle[0], circle[1])
            try:
                CharacterFinder.wait_for_info_card_to_appear()
            except TimedOutWhileWaitingForInfoCard:
                if not TurnDetector.is_ap_counter_visible():
                    return None # Fight ended.
                continue
            
            name_area = CharacterFinder.screenshot_name_area_on_info_card()
            if CharacterFinder.read_name_area_screenshot(name_area) != character_name:
                monster_locations.append(circle)
        
        move_mouse_off_game_area() # To prevent info card from blocking spell bar.
        return monster_locations

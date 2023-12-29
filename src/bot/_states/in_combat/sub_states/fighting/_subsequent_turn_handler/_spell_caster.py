from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import pyautogui as pyag

from utilities import move_mouse_off_game_area
from .._character_finder import Finder as CharacterFinder
from .._spells.spells import Spells
from src.bot._states.in_combat._status_enum import Status
from .._turn_detector import TurnDetector

class Caster:

    @classmethod
    def cast_spells(cls, character_name: str):
        log.info("Casting spells ...")
        if cls._is_any_core_spell_available():
            result = cls._handle_core_spells(character_name)
            if result != Status.SUCCESSFULLY_CAST_CORE_SPELLS:
                return Status.FAILED_TO_CAST_CORE_SPELLS
            
        if cls._is_any_non_core_spell_available():
            result = cls._handle_non_core_spells(character_name)
            if result != Status.SUCCESSFULLY_CAST_NON_CORE_SPELLS:
                return Status.FAILED_TO_CAST_NON_CORE_SPELLS

        log.info("Finished casting spells.")
        return Status.SUCCESSFULLY_FINISHED_SUBSEQUENT_TURN_SPELL_CASTING

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
        if isinstance(character_pos, Status):
            if (
                character_pos == Status.TIMED_OUT_WHILE_UNSHRINKING_TURN_BAR
                or character_pos == Status.TIMED_OUT_WHILE_WAITING_FOR_INFO_CARD_TO_APPEAR
            ):
                return Status.FAILED_TO_GET_CHARACTER_POS_BY_TURN_BAR
    
        while True:
            if Spells.EARTHQUAKE.is_available():
                result = Spells.EARTHQUAKE.cast(character_pos[0], character_pos[1])
                if result != Status.SUCCESSFULLY_CAST_SPELL:
                    return Status.FAILED_TO_CAST_SPELL
            elif Spells.POISONED_WIND.is_available():
                result = Spells.POISONED_WIND.cast(character_pos[0], character_pos[1])
                if result != Status.SUCCESSFULLY_CAST_SPELL:
                    return Status.FAILED_TO_CAST_SPELL
            elif Spells.SYLVAN_POWER.is_available():
                result = Spells.SYLVAN_POWER.cast(character_pos[0], character_pos[1])
                if result != Status.SUCCESSFULLY_CAST_SPELL:
                    return Status.FAILED_TO_CAST_SPELL
            if (
                not Spells.EARTHQUAKE.is_available()
                and not Spells.POISONED_WIND.is_available()
                and not Spells.SYLVAN_POWER.is_available()
            ):
                return Status.SUCCESSFULLY_CAST_CORE_SPELLS

    @classmethod
    def _handle_non_core_spells(cls, character_name: str):
        result = cls._handle_bramble(character_name)
        if result != Status.SUCCESSFULLY_HANDLED_BRAMBLE:
            return Status.FAILED_TO_CAST_NON_CORE_SPELLS
        return Status.SUCCESSFULLY_CAST_NON_CORE_SPELLS

    @classmethod
    def _handle_bramble(cls, character_name: str):
        while True:
            if not Spells.BRAMBLE.is_available():
                break

            monster_locations = cls._get_monster_locations(character_name)
            if monster_locations is None: # Fight ended.
                break
                
            for x, y in monster_locations:
                result = Spells.BRAMBLE.cast(x, y)
                if result == Status.SPELL_IS_NOT_CASTABLE_ON_PROVIDED_POS:
                    continue
                elif result == Status.SUCCESSFULLY_CAST_SPELL:
                    move_mouse_off_game_area()
                    break
                else:
                    return result
                
        move_mouse_off_game_area()
        return Status.SUCCESSFULLY_HANDLED_BRAMBLE

    @classmethod
    def _get_monster_locations(cls, character_name: str):
        monster_locations = []
        blue_circles = CharacterFinder.get_blue_circle_locations()
        for circle in blue_circles:
            pyag.moveTo(circle[0], circle[1])
            CharacterFinder.wait_for_info_card_to_appear()
            if not CharacterFinder.is_info_card_visible():
                if not TurnDetector.is_ap_counter_visible():
                    return None # Fight ended.
                log.error("Timed out while waiting for info card to appear while getting monster locations. Continuing to next circle ... ")
                continue
            
            name_area = CharacterFinder.screenshot_name_area_on_info_card()
            if CharacterFinder.read_name_area_screenshot(name_area) != character_name:
                monster_locations.append(circle)
        
        move_mouse_off_game_area() # To prevent info card from blocking spell bar.
        return monster_locations

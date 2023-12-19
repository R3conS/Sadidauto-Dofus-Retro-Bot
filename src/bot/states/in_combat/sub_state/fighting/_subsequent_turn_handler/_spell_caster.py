from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import pyautogui as pyag

from utilities import move_mouse_off_game_area
from .._spells import Spells
from ..status_enum import Status
from .._character_finder import Finder as CharacterFinder


class Caster:

    @classmethod
    def cast_spells(cls, character_name: str):
        if cls._is_any_core_spell_available():
            result = cls._handle_core_spells(character_name)
            if result != Status.SUCCESSFULLY_CAST_CORE_SPELLS:
                return Status.FAILED_TO_CAST_CORE_SPELLS
            
        if cls._is_any_non_core_spell_available():
            result = cls._handle_non_core_spells(character_name)
            if result != Status.SUCCESSFULLY_CAST_NON_CORE_SPELLS:
                return Status.FAILED_TO_CAST_NON_CORE_SPELLS

        return Status.SUCCESSFULLY_FINISHED_SUBSEQUENT_TURN_SPELL_CASTING

    @staticmethod
    def _is_any_core_spell_available():
        return (
            Spells.is_earthquake_available()
            or Spells.is_poisoned_wind_available()
            or Spells.is_sylvan_power_available()
        )

    @staticmethod
    def _is_any_non_core_spell_available():
        return Spells.is_bramble_available()

    @staticmethod
    def _handle_core_spells(character_name: str):
        character_pos = CharacterFinder.find_by_turn_bar(character_name)
        if (
            character_pos == Status.TIMED_OUT_WHILE_UNSHRINKING_TURN_BAR
            or character_pos == Status.FAILED_TO_GET_TURN_INDICATOR_ARROW_LOCATION
            or character_pos == Status.TIMED_OUT_WHILE_WAITING_FOR_INFO_CARD_TO_APPEAR
        ):
            return Status.FAILED_TO_GET_CHARACTER_POS_BY_TURN_BAR
    
        while True:
            if Spells.is_earthquake_available():
                result = Spells.cast_earthquake(character_pos[0], character_pos[1])
                if result != Status.SUCCESSFULLY_CAST_SPELL:
                    return Status.FAILED_TO_CAST_SPELL
            elif Spells.is_poisoned_wind_available():
                result = Spells.cast_poisoned_wind(character_pos[0], character_pos[1])
                if result != Status.SUCCESSFULLY_CAST_SPELL:
                    return Status.FAILED_TO_CAST_SPELL
            elif Spells.is_sylvan_power_available():
                result = Spells.cast_sylvan_power(character_pos[0], character_pos[1])
                if result != Status.SUCCESSFULLY_CAST_SPELL:
                    return Status.FAILED_TO_CAST_SPELL
            if (
                not Spells.is_earthquake_available()
                and not Spells.is_poisoned_wind_available()
                and not Spells.is_sylvan_power_available()
            ):
                return Status.SUCCESSFULLY_CAST_CORE_SPELLS

    @classmethod
    def _handle_non_core_spells(cls, character_name: str):
        result = cls._handle_bramble(character_name)
        if result != Status.SUCCESSFULLY_CAST_NON_CORE_SPELLS:
            return Status.FAILED_TO_CAST_NON_CORE_SPELLS
        return Status.SUCCESSFULLY_CAST_NON_CORE_SPELLS
        
    @classmethod
    def _handle_bramble(cls, character_name: str):
        monster_locations = cls._get_monster_locations(character_name)
        loc_i = 0
        while loc_i < len(monster_locations):
            if Spells.is_bramble_available():
                result = Spells.cast_bramble(monster_locations[loc_i][0], monster_locations[loc_i][1])
                if result == Status.SPELL_IS_NOT_CASTABLE_ON_PROVIDED_POS:
                    loc_i += 1
                    continue
                elif result == Status.SUCCESSFULLY_CAST_SPELL:
                    move_mouse_off_game_area()
                    monster_locations = cls._get_monster_locations(character_name)
                    loc_i = 0
                else:
                    return result
            else:
                break
        move_mouse_off_game_area()
        return Status.SUCCESSFULLY_CAST_NON_CORE_SPELLS
                
    @classmethod
    def _get_monster_locations(cls, character_name: str):
        monster_locations = []
        red_circles = CharacterFinder.get_red_circle_locations()
        blue_circles = CharacterFinder.get_blue_circle_locations()
        for circle in red_circles + blue_circles:
            pyag.moveTo(circle[0], circle[1])
            CharacterFinder.wait_for_info_card_to_appear()
            if not CharacterFinder.is_info_card_visible():
                log.error("Timed out while waiting for info card to appear while getting monster locations. Continuing to next circle ... ")
                continue
            
            name_area = CharacterFinder.screenshot_name_area_on_info_card()
            if CharacterFinder.read_name_area_screenshot(name_area) != character_name:
                monster_locations.append(circle)
        
        move_mouse_off_game_area() # To prevent info card from blocking spell bar.
        return monster_locations

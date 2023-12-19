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
        if cls.is_any_core_spell_available():
            result = cls._handle_core_spells(character_name)
            if result != Status.SUCCESSFULLY_CAST_CORE_SPELLS:
                return Status.FAILED_TO_CAST_CORE_SPELLS
            
        if cls.is_any_non_core_spell_available():
            result = cls._handle_non_core_spells(character_name)
            if result != Status.SUCCESSFULLY_CAST_NON_CORE_SPELLS:
                return Status.FAILED_TO_CAST_NON_CORE_SPELLS

        # ToDo: Implement the rest.

    @staticmethod
    def is_any_core_spell_available():
        return (
            Spells.is_earthquake_available()
            or Spells.is_poisoned_wind_available()
            or Spells.is_sylvan_power_available()
        )

    @staticmethod
    def is_any_non_core_spell_available():
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

    @staticmethod
    def _handle_non_core_spells(character_name: str):
        character_pos = CharacterFinder.find_by_circles(character_name)
        if character_pos == Status.TIMED_OUT_WHILE_WAITING_FOR_INFO_CARD_TO_APPEAR:
            return Status.FAILED_TO_GET_CHARACTER_POS_BY_CIRCLES
        
        # ToDo: Implement.
        pass

    def _handle_bramble(self):
        # ToDo: Implement. Logic is in .drawio file in "Downloads".
        # Or maybe in google drive folder.
        pass

    @classmethod
    def _get_monster_locations(cls, character_name: str):
        monster_locations = []
        turn_card_locations = cls._get_turn_card_locations()
        for location in turn_card_locations:
            pyag.moveTo(location[0], location[1])
            CharacterFinder.wait_for_info_card_to_appear()
            if not CharacterFinder.is_info_card_visible():
                log.info("Timed out while waiting for info card to appear while getting monster locations.")
                return Status.TIMED_OUT_WHILE_WAITING_FOR_INFO_CARD_TO_APPEAR
            
            name_area = CharacterFinder.screenshot_name_area_on_info_card()
            if CharacterFinder.read_name_area_screenshot(name_area) == character_name:
                turn_card_locations.remove(location)
                monster_locations = turn_card_locations
                break
            
        move_mouse_off_game_area() # To prevent info card from blocking spell bar.
        return monster_locations

    @staticmethod
    def _get_turn_card_locations():
        """From most left to most right card. Top left corner of each card."""

        # ToDo: Implement a more consistent way of getting turn card locations.

        all_turn_card_locations = [
            (269, 548), (309, 548), (349, 548), (389, 548), 
            (429, 548), (469, 548), (509, 548), (549, 548), 
            (589, 548), (629, 548), (669, 548), (709, 548), 
            (749, 548), (789, 548), (829, 548), (869, 548)
        ]
        locations = []
        for location in all_turn_card_locations:
            if pyag.pixelMatchesColor(location[0], location[1], (255, 255, 255)):
                locations.append(location)
        return locations

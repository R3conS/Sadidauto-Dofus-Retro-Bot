from src.logger import get_logger

log = get_logger()

import glob
import os
from time import perf_counter, sleep

import cv2
import pyautogui as pyag

from src.bot._exceptions import RecoverableException
from src.bot._interfaces.interfaces import Interfaces
from src.bot._map_changer.map_changer import MapChanger
from src.bot._states.out_of_combat._pods_reader.reader import PodsReader
from src.bot._states.out_of_combat._status_enum import Status
from src.bot._states.out_of_combat._sub_states.banking.bank_data import Getter as BankDataGetter
from src.bot._states.out_of_combat._sub_states.hunting._hp_recoverer.hp_recoverer import HpRecoverer
from src.bot._states.out_of_combat._sub_states.hunting._map_data.getter import Getter as MapDataGetter
from src.bot._states.out_of_combat._sub_states.hunting._monster_location_finder import MonsterLocationFinder
from src.bot._states.out_of_combat._sub_states.hunting._monster_tooltip_finder.monster_tooltip_finder import MonsterTooltipFinder, Tooltip
from src.utilities.general import load_image_full_path, move_mouse_off_game_area, save_image_to_debug_folder
from src.utilities.image_detection import ImageDetection
from src.utilities.screen_capture import ScreenCapture


class Hunter:

    IMAGE_FOLDER_PATH = "src\\bot\\_states\\out_of_combat\\_sub_states\\hunting\\_images"

    READY_BUTTON_AREA = (678, 507, 258, 91)
    READY_BUTTON_IMAGES = [
        load_image_full_path(path) 
        for path in glob.glob(os.path.join(IMAGE_FOLDER_PATH, "ready_button\\*.png"))
    ]

    CLICKED_ON_JOIN_SWORD_IMAGES = [
        load_image_full_path(path)
        for path in glob.glob(os.path.join(IMAGE_FOLDER_PATH, "clicked_on_join_sword\\*.png"))
    ]

    ATTACK_TOOLTIP_IMAGES = [
        load_image_full_path(path)
        for path in glob.glob(os.path.join(IMAGE_FOLDER_PATH, "attack\\*.png"))
    ]
    
    FORBIDDEN_MONSTERS = ["Frakacia Leukocytine"]

    def __init__(self, script: str, go_bank_when_pods_percentage: int = 90):
        self._script = script
        self._check_pods_every_x_fights = 5
        self._consecutive_fights_counter = self._check_pods_every_x_fights
        self._total_fights_counter = 0
        self._pods_percentage_limit = go_bank_when_pods_percentage
        map_data = MapDataGetter.get_data_object(self._script)
        self._pathing_data = map_data.get_pathing_data()
        self._map_type_data = map_data.get_map_type_data()
        bank_data = BankDataGetter.get_data(self._script)
        self._bank_map_coords = bank_data["bank_map"]
        self._is_char_inside_bank: callable = bank_data["is_char_inside_bank"]
        self._bank_exit_coords = bank_data["exit_coords"]
        self._forbidden_monster_group_locations = []

    def hunt(self):
        while True:
            if self._consecutive_fights_counter >= self._check_pods_every_x_fights:
                pods_percentage = self._get_pods_percentage()
                self._consecutive_fights_counter = 0
                if pods_percentage >= self._pods_percentage_limit:
                    log.info(f"Reached pods limit of: {self._pods_percentage_limit}%. Going to bank ... ")
                    # Setting these values to equal so that pods are checked on 
                    # the first call to 'hunt()' after banking.
                    self._consecutive_fights_counter = self._check_pods_every_x_fights
                    return Status.REACHED_PODS_LIMIT

            if not HpRecoverer.is_health_bar_full():
                HpRecoverer.recover_all_health_by_sitting()

            map_coords = MapChanger.get_current_map_coords()
            if map_coords == self._bank_map_coords and self._is_char_inside_bank():
                log.info("Character is inside the bank.")
                self._leave_bank()

            map_type = self._map_type_data[map_coords]
            if map_type == "traversable":
                result = self._handle_traversable_map(map_coords)
                if result == Status.SUCCESSFULLY_TRAVERSED_MAP:
                    continue
            elif map_type == "fightable":
                while True:
                    result = self._handle_fightable_map(map_coords)
                    if result == Status.SUCCESSFULLY_ATTACKED_MONSTER:
                        self._forbidden_monster_group_locations.clear()
                        return Status.SUCCESSFULLY_ATTACKED_MONSTER
                    elif result == Status.MAP_FULLY_SEARCHED:
                        self._forbidden_monster_group_locations.clear()
                        break
                    elif (
                        result == Status.TIMED_OUT_WHILE_ATTACKING_MONSTER
                        or result == Status.MONSTER_IS_NO_LONGER_AT_LOCATION
                        or result == Status.ATTACK_TOOLTIP_NOT_FOUND
                        or result == Status.MAP_WAS_CHANGED_BY_ACCIDENT
                        or result == Status.ENTERED_LUMBERJACKS_WORKSHOP_BY_ACCIDENT
                    ):
                        continue

    def _get_pods_percentage(self):
        log.info("Getting inventory pods percentage ... ")
        Interfaces.INVENTORY.open()
        percentage = PodsReader.INVENTORY.get_occupied_percentage()
        log.info(f"Inventory is {percentage}% full.")
        Interfaces.INVENTORY.close()
        return percentage

    def _handle_traversable_map(self, map_coords):
        MapChanger.change_map(map_coords, self._pathing_data[map_coords])
        return Status.SUCCESSFULLY_TRAVERSED_MAP
    
    def _handle_fightable_map(self, map_coords):
        log.info(f"Hunting on map: '{map_coords}' ... ")

        monster_tooltips = MonsterTooltipFinder.find_tooltips()
        for tooltip in monster_tooltips:
            log.info(f"Found monster group: {tooltip.monster_counts_as_str}.")

            if self._is_monster_group_location_forbidden(tooltip):
                log.info("Skipping monster group because its location is forbidden ... ")
                continue

            if self._does_tooltip_contain_forbidden_monsters(tooltip):
                log.info("Skipping monster group because it contains forbidden monsters ... ")
                continue

            monster_location = MonsterLocationFinder.get_monster_location(tooltip)
            if monster_location is None:
                log.error(
                    "Skipping monster group because finding the location of an "
                    "attackable monster around the tooltip failed."
                )
                continue

            result = self._attack(monster_location)

            if result == Status.SUCCESSFULLY_ATTACKED_MONSTER:
                self._consecutive_fights_counter += 1
                self._total_fights_counter += 1
                # If a need arises to change the format of any of these
                # messages make sure to update the associated parsing
                # function that is used to read them for logging in the
                # bot counters log window. The functions are a part of 
                # the BotCountersPlainTextEdit class.
                log.info(f"Successfully attacked: {tooltip.monster_counts_as_str}.")
                log.info(f"Started fight number: '{self._total_fights_counter}'.")
                return Status.SUCCESSFULLY_ATTACKED_MONSTER

            elif result == Status.MONSTER_IS_NO_LONGER_AT_LOCATION:
                wait_time = 3
                log.info(
                    "Monster group is no longer at its initial location. "
                    f"Waiting {wait_time} seconds to make sure it stops "
                    "moving in case it moved."
                )
                sleep(wait_time)
                return Status.MONSTER_IS_NO_LONGER_AT_LOCATION

            elif result == Status.ATTACK_TOOLTIP_NOT_FOUND:
                log.info(
                    "Failed to find 'Attack' tooltip. The monster group "
                    "was most likely attacked by someone else."
                )
                self._add_monster_group_location_to_forbidden_locations(tooltip)
                return Status.ATTACK_TOOLTIP_NOT_FOUND

            # Can happen if:
            # 1) the character is standing on the same spot as the monster
            # that is being attacked.
            # 2) if the attacked monster is standing on the map change sun.
            elif result == Status.TIMED_OUT_WHILE_ATTACKING_MONSTER:
                self._add_monster_group_location_to_forbidden_locations(tooltip)
                if self._was_map_changed_by_accident(map_coords):
                    log.info("Map was changed while attacking the monster.")
                    self._change_map_back_to_original(map_coords)
                    return Status.MAP_WAS_CHANGED_BY_ACCIDENT
                elif self._is_char_in_lumberjack_workshop():
                    log.info("Entered 'Lumberjack's Workshop' while attacking the monster.")
                    self._leave_lumberjacks_workshop()
                    return Status.ENTERED_LUMBERJACKS_WORKSHOP_BY_ACCIDENT
                return Status.TIMED_OUT_WHILE_ATTACKING_MONSTER

        log.info(f"Map '{map_coords}' fully searched.")
        MapChanger.change_map(map_coords, self._pathing_data[map_coords])

        return Status.MAP_FULLY_SEARCHED

    def _add_monster_group_location_to_forbidden_locations(self, tooltip: Tooltip):
        self._forbidden_monster_group_locations.append(tooltip.level_text_center_point)

    @staticmethod
    def _was_map_changed_by_accident(current_map_coords):
        return current_map_coords != MapChanger.get_current_map_coords()

    def _is_monster_group_location_forbidden(self, tooltip: Tooltip):
        return tooltip.level_text_center_point in self._forbidden_monster_group_locations

    @classmethod
    def _does_tooltip_contain_forbidden_monsters(cls, tooltip: Tooltip):
        for monster in cls.FORBIDDEN_MONSTERS:
            if monster in tooltip.monster_counts_as_str:
                log.info(f"Monster group contains a forbidden monster: {monster}.")
                return True
        return False

    @classmethod
    def _wait_for_ready_button_to_appear(cls, timeout=8):
        start_time = perf_counter()
        while perf_counter() - start_time <= timeout:
            if cls._is_ready_button_visible():
                return 
            sleep(0.25)
        raise TimeoutError("Timed out while waiting for 'Ready' button to appear.")

    def _attack(self, monster_location: tuple[int, int]):
        log.info(f"Attacking monster at: {monster_location} ... ")

        pyag.moveTo(*monster_location)
        if MonsterLocationFinder.is_monster_tooltip_visible_around_point(monster_location):
            pyag.click()
            sleep(0.05) # Give some time for the tooltip to appear.

            if self._is_attack_tooltip_visible():
                pyag.moveTo(*self._get_attack_tooltip_pos())
                pyag.click()
                # ToDo: instead of moving mouse of the game area, keep it hovered
                # and check if the monster tooltip is still present. If it is
                # - check if it has stars. If it doesn't it means that
                # the monster was attacked already. It can be done in the
                # wait for ready button to appear loop.
                move_mouse_off_game_area()
                try:
                    self._wait_for_ready_button_to_appear()
                    return Status.SUCCESSFULLY_ATTACKED_MONSTER
                except TimeoutError:
                    return Status.TIMED_OUT_WHILE_ATTACKING_MONSTER
            else:
                # Close any tooltips that might've been opened like
                # "Join", "Cut", other player's option menu etc.
                move_mouse_off_game_area()
                pyag.click()
                return Status.ATTACK_TOOLTIP_NOT_FOUND

        else:
            return Status.MONSTER_IS_NO_LONGER_AT_LOCATION

    @classmethod
    def _is_join_tooltip_visible(cls):
        if len(
            ImageDetection.find_images(
                haystack=ScreenCapture.custom_area((0, 50, 937, 550)),
                needles=cls.CLICKED_ON_JOIN_SWORD_IMAGES,
                confidence=0.99,
                method=cv2.TM_SQDIFF_NORMED
            )
        ) > 0:
            return True
        return False  

    @classmethod
    def _is_attack_tooltip_visible(cls):
        if len(
            ImageDetection.find_images(
                haystack=ScreenCapture.custom_area((0, 50, 937, 550)),
                needles=cls.ATTACK_TOOLTIP_IMAGES,
                confidence=0.99,
                method=cv2.TM_SQDIFF_NORMED
            )
        ) > 0:
            return True
        return False 
    
    @classmethod
    def _get_attack_tooltip_pos(cls):
        rectangle = ImageDetection.find_images(
            haystack=ScreenCapture.custom_area((0, 0, 937, 600)),
            needles=cls.ATTACK_TOOLTIP_IMAGES,
            confidence=0.98,
            method=cv2.TM_SQDIFF_NORMED
        )
        if len(rectangle) > 0:
            return ImageDetection.get_rectangle_center_point(rectangle[0])
        raise RecoverableException("Failed to get 'Attack' tooltip position.")

    @classmethod
    def _is_ready_button_visible(cls):
        if len(
            ImageDetection.find_images(
                haystack=ScreenCapture.custom_area(cls.READY_BUTTON_AREA),
                needles=cls.READY_BUTTON_IMAGES,
                confidence=0.85,
                method=cv2.TM_SQDIFF_NORMED
            )
        ) > 0:
            return True
        return False  

    @staticmethod
    def _is_char_in_lumberjack_workshop():
        return all ((
            pyag.pixelMatchesColor(49, 559, (0, 0, 0)),
            pyag.pixelMatchesColor(48, 137, (0, 0, 0)),
            pyag.pixelMatchesColor(782, 89, (0, 0, 0)),
            pyag.pixelMatchesColor(820, 380, (0, 0, 0)),
            pyag.pixelMatchesColor(731, 554, (0, 0, 0)),
        ))

    @staticmethod
    def _leave_lumberjacks_workshop():
        log.info("Leaving 'Lumberjack's Workshop'.")
        pyag.keyDown("e")
        pyag.moveTo(667, 507)
        pyag.click()
        pyag.keyUp("e")
        MapChanger.wait_loading_screen_pass()
        if not Hunter._is_char_in_lumberjack_workshop():
            log.info("Successfully left 'Lumberjack's Workshop'.")
            return
        raise RecoverableException("Failed to leave 'Lumberjack's Workshop'.")

    def _leave_bank(self):
        log.info("Attempting to leave the bank ... ")
        pyag.keyDown('e')
        pyag.moveTo(*self._bank_exit_coords)
        pyag.click()
        pyag.keyUp('e')
        MapChanger.wait_loading_screen_pass()
        if not self._is_char_inside_bank():
            log.info("Successfully left the bank.")
            return 
        raise RecoverableException("Failed to leave the bank.")

    @staticmethod
    def _change_map_back_to_original(original_map_coords):
        log.info("Changing map back to original ...")
        MapChanger.change_map(MapChanger.get_current_map_coords(), original_map_coords)
        log.info("Successfully changed map back to original!")


if __name__ == "__main__":
    hunter = Hunter("af_anticlock")
    hunter.hunt()

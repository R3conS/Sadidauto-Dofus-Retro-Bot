from src.logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import glob
from time import perf_counter, sleep
import os

import cv2
import pyautogui as pyag

from image_detection import ImageDetection
from screen_capture import ScreenCapture
from src.utilities import load_image_full_path, move_mouse_off_game_area
from src.bot._exceptions import RecoverableException
from src.bot._interfaces.interfaces import Interfaces
from src.bot._map_changer.map_changer import MapChanger
from src.bot._states.out_of_combat._pods_reader.reader import PodsReader
from src.bot._states.out_of_combat._status_enum import Status
from src.bot._states.out_of_combat._sub_states.hunting._map_data.getter import Getter as MapDataGetter
from src.bot._states.out_of_combat._sub_states.banking.bank_data import Getter as BankDataGetter


class Hunter:

    IMAGE_FOLDER_PATH = "src\\bot\\_states\\out_of_combat\\_sub_states\\hunting\\_images"
    READY_BUTTON_AREA = (678, 507, 258, 91)
    READY_BUTTON_IMAGES = [
        load_image_full_path(path) 
        for path in glob.glob(os.path.join(IMAGE_FOLDER_PATH, "ready_button\\*.png"))
    ]
    JOIN_SWORD_IMAGES = [
        load_image_full_path(path) 
        for path in glob.glob(os.path.join(IMAGE_FOLDER_PATH, "join_sword\\*.png"))
    ]
    JOIN_SWORD_IMAGE_MASKS = ImageDetection.create_masks(JOIN_SWORD_IMAGES)

    def __init__(self, script: str, game_window_title: str):
        self._script = script
        self._game_window_title = game_window_title
        self._check_pods_every_x_fights = 5
        self._consecutive_fights_counter = self._check_pods_every_x_fights
        self._pods_percentage_limit = 90
        # Map data
        map_data = MapDataGetter.get_data_object(self._script)
        self._pathing_data = map_data.get_pathing_data()
        self._map_type_data = map_data.get_map_type_data()
        # Monster data
        monster_images = self._load_monster_images()
        monster_image_masks = ImageDetection.create_masks(monster_images)
        segment_size = 4
        self._segmented_monster_images = self._segment_data(monster_images, segment_size)
        self._segmented_monster_image_masks = self._segment_data(monster_image_masks, segment_size)
        # Bank data
        bank_data = BankDataGetter.get_data(self._script)
        self._bank_map_coords = bank_data["bank_map"]
        self._is_char_inside_bank: callable = bank_data["is_char_inside_bank"]
        self._bank_exit_coords = bank_data["exit_coords"]

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

            map_coords = MapChanger.get_current_map_coords()
            if map_coords == self._bank_map_coords:
                log.info("Character is inside the bank.")
                self._leave_bank()

            map_type = self._map_type_data[map_coords]
            if map_type == "traversable":
                result = self._handle_traversable_map(map_coords)
                if result == Status.SUCCESSFULLY_TRAVERSED_MAP:
                    continue
            elif map_type == "fightable":
                result = self._handle_fightable_map(map_coords)
                if result == Status.SUCCESSFULLY_ATTACKED_MONSTER:
                    return Status.SUCCESSFULLY_ATTACKED_MONSTER
                elif result == Status.MAP_FULLY_SEARCHED:
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
        if MapChanger.has_loading_screen_passed():
            return Status.SUCCESSFULLY_TRAVERSED_MAP
        raise RecoverableException("Failed to traverse map.")
    
    def _handle_fightable_map(self, map_coords):
        log.info(f"Hunting on map: {map_coords} ... ")
        haystack_image = ScreenCapture.game_window()
        for image_segment, mask_segment in zip(self._segmented_monster_images, self._segmented_monster_image_masks):
            matches = self._search_segment(image_segment, mask_segment, haystack_image)
            if len(matches) > 0:
                monster_x, monster_y = matches[0][0], matches[0][1]
                log.info(f"Found monster at {monster_x, monster_y}.")

                if self._is_join_sword_on_pos(monster_x, monster_y):
                    log.info("Monster was attacked by someone else. Skipping ... ")
                    continue

                self._attack(monster_x, monster_y)
                # Allow time for 'Right Click Menu' to open in case the attack 
                # click missed. Clicks can miss if the monster moves away.
                sleep(0.25) # Maybe increase this to 0.5?
                if Interfaces.RIGHT_CLICK_MENU.is_open():
                    log.error("Failed to attack monster because it moved away. Skipping ... ")
                    Interfaces.RIGHT_CLICK_MENU.close()
                    continue

                if self._is_attack_successful():
                    self._consecutive_fights_counter += 1
                    return Status.SUCCESSFULLY_ATTACKED_MONSTER
                else:
                    # Clicking off the game area after a failed attack to
                    # close any unwanted tooltips like 'Cut' a tree or another
                    # character's option menu.
                    move_mouse_off_game_area()
                    pyag.click()
                    if map_coords != MapChanger.get_current_map_coords():
                        log.error("Map was accidentally changed during the attack.")
                        self._change_map_back_to_original(map_coords)
                        continue
                    elif self._is_char_in_lumberjack_workshop():
                        log.info("Character is in 'Lumberjack's Workshop'. Leaving ... ")
                        self._leave_lumberjacks_workshop()
                        continue

        log.info(f"Map {map_coords} fully searched. Changing map ... ")
        MapChanger.change_map(map_coords, self._pathing_data[map_coords])
        if MapChanger.has_loading_screen_passed():
            return Status.MAP_FULLY_SEARCHED
        raise RecoverableException("Failed to change map.")

    def _load_monster_images(self):
        if "af_" in self._script:
            folder_path =  os.path.join(self.IMAGE_FOLDER_PATH, "monster\\astrub_forest")
        return [load_image_full_path(path) for path in glob.glob(os.path.join(folder_path, "*.png"))]

    @staticmethod
    def _segment_data(data: list, segment_size) -> list[list]:
        segments = []
        for i in range(0, len(data), segment_size):
            segments.append(data[i:i + segment_size])
        return segments

    @staticmethod
    def _search_segment(image_segment, mask_segment, haystack_image) -> list[tuple[int, int]]:
        matches = ImageDetection.find_images(
            haystack=haystack_image,
            needles=image_segment,
            confidence=0.9837,
            method=cv2.TM_CCORR_NORMED,
            masks=mask_segment,
            remove_alpha_channels=True
        )
        click_coords = []
        for match in matches:
            if len(match) > 0:
                click_coords.append(ImageDetection.get_rectangle_center_point(match))
        return click_coords

    def _attack(self, monster_x, monster_y):
        log.info(f"Attacking monster at {monster_x, monster_y} ... ")
        pyag.moveTo(monster_x, monster_y)
        if "Dofus Retro" in self._game_window_title:
            pyag.click(button="right")
        else: # For Abrak private server
            pyag.keyDown("shift")
            pyag.click()
            pyag.keyUp("shift")

    @classmethod
    def _is_attack_successful(cls):
        start_time = perf_counter()
        while perf_counter() - start_time <= 6:
            if len(
                ImageDetection.find_images(
                    haystack=ScreenCapture.custom_area(cls.READY_BUTTON_AREA),
                    needles=cls.READY_BUTTON_IMAGES,
                    confidence=0.98,
                    method=cv2.TM_SQDIFF_NORMED
                )
            ) > 0:
                log.info("Attack successful.")
                return True
        log.error("Attack failed.")
        return False  

    @classmethod
    def _is_join_sword_on_pos(cls, x, y):
        if len(
            ImageDetection.find_images(
                haystack=ScreenCapture.around_pos((x, y), 65),
                needles=cls.JOIN_SWORD_IMAGES,
                confidence=0.98,
                method=cv2.TM_CCORR_NORMED,
                masks=cls.JOIN_SWORD_IMAGE_MASKS
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
        pyag.keyDown("e")
        pyag.moveTo(667, 507)
        pyag.click()
        pyag.keyUp("e")
        if MapChanger.has_loading_screen_passed():
            log.info("Successfully left 'Lumberjack's Workshop'.")
            return
        # ToDo: If recovery fails multiple times then maybe emergency
        # recall teleport?
        raise RecoverableException("Failed to leave 'Lumberjack's Workshop'.")

    def _leave_bank(self):
        log.info("Attempting to leave the bank ... ")
        pyag.keyDown('e')
        pyag.moveTo(*self._bank_exit_coords)
        pyag.click()
        pyag.keyUp('e')
        if MapChanger.has_loading_screen_passed():
            if not self._is_char_inside_bank():
                log.info("Successfully left the bank.")
                return 
            raise RecoverableException("Failed to leave the bank.")
        raise RecoverableException("Failed to detect loading screen after trying to leave the bank.")

    @staticmethod
    def _change_map_back_to_original(original_map_coords):
        log.info("Attempting to change map back to original ...")
        MapChanger.change_map(MapChanger.get_current_map_coords(), original_map_coords)
        if MapChanger.has_loading_screen_passed():
            log.info("Successfully changed map back to original!")
            return
        raise RecoverableException("Failed to change map back to original map.")

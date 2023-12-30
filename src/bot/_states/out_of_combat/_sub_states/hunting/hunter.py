from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter, sleep
import os

import cv2
import pyautogui as pyag

from image_detection import ImageDetection
from screen_capture import ScreenCapture
from src.utilities import load_image
from ._map_data.getter import Getter as MapDataGetter
from ..banking.bank_data import Getter as BankDataGetterGetter
from src.bot._interfaces.interfaces import Interfaces
from src.bot._map_changer.map_changer import MapChanger
from src.bot._states.out_of_combat._pods_reader.reader import PodsReader
from src.bot._states.out_of_combat._status_enum import Status
from src.bot._exceptions import RecoverableException


class Hunter:

    IMAGE_FOLDER_PATH = "src\\bot\\_states\\out_of_combat\\_sub_states\\hunting\\_images"
    READY_BUTTON_AREA = (678, 507, 258, 91)
    READY_BUTTON_LIT_IMAGE = load_image(IMAGE_FOLDER_PATH, "ready_button_lit.png")
    READY_BUTTON_LIT_IMAGE_MASK = ImageDetection.create_mask(READY_BUTTON_LIT_IMAGE)
    READY_BUTTON_DIM_IMAGE = load_image(IMAGE_FOLDER_PATH, "ready_button_dim.png")
    READY_BUTTON_DIM_IMAGE_MASK = ImageDetection.create_mask(READY_BUTTON_DIM_IMAGE)

    def __init__(self, script: str, game_window_title: str):
        self._game_window_title = game_window_title
        self._check_pods_every_x_fights = 5
        self._consecutive_fights_counter = self._check_pods_every_x_fights
        self._pods_percentage_limit = 90
        # Map data
        map_data = MapDataGetter.get_data_object(script)
        self._pathing_data = map_data.get_pathing_data()
        self._map_type_data = map_data.get_map_type_data()
        self._monster_image_data = self._load_monster_image_data()
        self._join_sword_detection_data = self._load_join_sword_detection_data()
        # Bank data
        bank_data = BankDataGetterGetter.get_data(script)
        self._bank_map_coords = bank_data["bank_map"]
        self._is_char_inside_bank: callable = bank_data["is_char_inside_bank"]
        self._bank_exit_coords = bank_data["exit_coords"]

    def hunt(self):
        while True:
            try:
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
            except RecoverableException:
                # ToDo: Call recovery code and try again a few times before
                # raising UnrecoverableException.
                log.error("Recoverable exception occurred while hunting. Exiting ...")
                os._exit(1)

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
        for segment_index in range(len(self._monster_image_data[0])):
            matches = self._search_segment(segment_index, ScreenCapture.game_window())
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

    def _load_monster_image_data(self):
        image_folder_path = "src\\bot\\_states\\out_of_combat\\_sub_states\\hunting\\_images\\monster_images"
        image_names = [
            "Boar_BL_1.png", "Boar_BR_1.png", "Boar_TL_1.png", "Boar_TR_1.png",
            "Pres_BL_1.png", "Pres_BR_1.png", "Pres_TL_1.png", "Pres_TR_1.png",
            "Pres_BL_2.png", "Pres_BR_2.png",
            "Mosk_BL_1.png", "Mosk_BR_1.png", "Mosk_TL_1.png", "Mosk_TR_1.png",
            "Mosk_BR_2.png", "Mosk_BL_2.png",
            "Mush_BL_1.png", "Mush_BR_1.png", "Mush_TL_1.png", "Mush_TR_1.png",
            "Mush_BL_2.png", "Mush_BR_2.png", "Mush_TL_2.png", "Mush_TR_2.png",
            "Wolf_BL_1.png", "Wolf_BR_1.png", "Wolf_TL_1.png", "Wolf_TR_1.png",
        ]
        loaded_images = []
        for name in image_names:
            path = os.path.join(image_folder_path, name)
            if not os.path.exists(path):
                raise FileNotFoundError(f"Image path '{path}' does not exist.")
            loaded_images.append(cv2.imread(path, cv2.IMREAD_UNCHANGED))
        return (
            self._segment_data(loaded_images, 4),
            self._segment_data(ImageDetection.create_masks(loaded_images), 4)
        )

    def _load_join_sword_detection_data(self):
        paths = [
            "src\\bot\\_states\\out_of_combat\\_sub_states\\hunting\\_images\\j_sword_ally_1.png",
            "src\\bot\\_states\\out_of_combat\\_sub_states\\hunting\\_images\\j_sword_ally_2.png",
            "src\\bot\\_states\\out_of_combat\\_sub_states\\hunting\\_images\\j_sword_ally_3.png",
            "src\\bot\\_states\\out_of_combat\\_sub_states\\hunting\\_images\\j_sword_enemy.png",
        ]
        read_images = []
        for path in paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Image path '{path}' does not exist.")
            read_images.append(cv2.imread(path, cv2.IMREAD_UNCHANGED))
        return read_images, ImageDetection.create_masks(read_images)

    def _segment_data(self, data: list, segment_size) -> list[list]:
        segments = []
        for i in range(0, len(data), segment_size):
            segments.append(data[i:i + segment_size])
        return segments

    def _search_segment(self, segment_index, haystack_image) -> list[tuple[int, int]]:
        images_segment = self._monster_image_data[0][segment_index]
        masks_segment = self._monster_image_data[1][segment_index]
        matches = ImageDetection.find_images(
            haystack=haystack_image,
            needles=images_segment,
            confidence=0.9837,
            method=cv2.TM_CCORR_NORMED,
            masks=masks_segment,
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
                    needles=[cls.READY_BUTTON_LIT_IMAGE, cls.READY_BUTTON_DIM_IMAGE],
                    confidence=0.99,
                    method=cv2.TM_CCORR_NORMED,
                    masks=[cls.READY_BUTTON_LIT_IMAGE_MASK, cls.READY_BUTTON_DIM_IMAGE_MASK],
                )
            ) > 0:
                log.info("Attack successful.")
                return True
        log.error("Attack failed.")
        return False  

    def _is_join_sword_on_pos(self, x, y):
        haystack = ScreenCapture.around_pos((x, y), 65)
        for i, image in enumerate(self._join_sword_detection_data[0]):
            result = ImageDetection.find_image(
                haystack,
                image,
                confidence=0.98,
                method=cv2.TM_CCORR_NORMED,
                mask=self._join_sword_detection_data[1][i],
                remove_alpha_channels=True
            )
            if len(result) > 0:
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

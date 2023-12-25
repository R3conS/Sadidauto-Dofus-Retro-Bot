from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter, sleep
import os

import cv2
import pyautogui as pyag

from image_detection import ImageDetection
from src.bot.interfaces.interfaces import Interfaces
from .map_data.getter import Getter as MapDataGetter
from screen_capture import ScreenCapture
from src.bot.map_changer.map_changer import MapChanger
from .status_enum import Status
from src.bot.states.out_of_combat.pods_reader.pods_reader import PodsReader


class Hunter:

    def __init__(self, script: str, game_window_title: str):
        self._game_window_title = game_window_title
        self._check_pods_every_x_fights = 5
        self._consecutive_fights_counter = self._check_pods_every_x_fights
        self._pods_percentage_limit = 90
        # Map data
        map_data = MapDataGetter.get_data_object(script)
        self._pathing_data = map_data.get_pathing_data()
        self._map_type_data = map_data.get_map_type_data()
        self._monster_detection_data = self._get_monster_detection_data()
        self._join_sword_detection_data = self._get_join_sword_detection_data()

    def hunt(self):
        while True:
            if self._consecutive_fights_counter >= self._check_pods_every_x_fights:
                pods_percentage = self._get_pods_percentage()
                if pods_percentage is not None:
                    self._consecutive_fights_counter = 0
                    if pods_percentage >= self._pods_percentage_limit:
                        log.info(f"Reached pods limit of: {self._pods_percentage_limit}%. Going to bank ... ")
                        # Setting these values to equal so that pods are checked on the 
                        # first call to 'hunt()' after banking.
                        self._consecutive_fights_counter = self._check_pods_every_x_fights
                        return Status.REACHED_PODS_LIMIT
                else:
                    return Status.FAILED_TO_FINISH_HUNTING

            map_coords = MapChanger.get_current_map_coords()
            map_type = self._map_type_data[map_coords]
            if map_type == "traversable":
                if self._handle_traversable_map(map_coords) == Status.FAILED_TO_TRAVERSE_MAP:
                    return Status.FAILED_TO_FINISH_HUNTING
            elif map_type == "fightable":
                log.info(f"Hunting on map: {map_coords} ... ")
                status = self._handle_fightable_map(map_coords)
                if status == Status.SUCCESSFULLY_STARTED_COMBAT:
                    return Status.SUCCESSFULLY_FINISHED_HUNTING
                elif status == Status.FAILED_TO_CHANGE_MAP_BACK_TO_ORIGINAL:
                    return Status.FAILED_TO_FINISH_HUNTING
                elif (
                    status == Status.FAILED_TO_CHANGE_MAP
                    or status == Status.FAILED_TO_LEAVE_LUMBERJACK_WORKSHOP
                ):
                    return Status.FAILED_TO_FINISH_HUNTING

    def _get_pods_percentage(self):
        log.info("Getting inventory pods percentage ... ")
        Interfaces.open_inventory()
        if Interfaces.is_inventory_open():
            percentage = PodsReader.get_occupied_inventory_percentage()
            if percentage is not None:
                log.info(f"Inventory is {percentage}% full.")
                Interfaces.close_inventory()
                if not Interfaces.is_inventory_open():
                    return percentage
            else:
                log.error("Failed to get inventory pods percentage.")
                PodsReader.save_images_for_debug()
        return None

    def _handle_traversable_map(self, map_coords):
        MapChanger.change_map(map_coords, self._pathing_data[map_coords])
        if MapChanger.has_loading_screen_passed():
            return Status.SUCCESSFULLY_TRAVERSED_MAP
        log.error("Failed to detect loading screen after changing map.")
        return Status.FAILED_TO_TRAVERSE_MAP

    def _handle_fightable_map(self, map_coords):
        for segment_index in range(len(self._monster_detection_data[0])):
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
                if Interfaces.is_right_click_menu_open():
                    log.error("Failed to attack monster because it moved away. Skipping ... ")
                    Interfaces.close_right_click_menu()
                    continue

                if self._is_attack_successful():
                    self._consecutive_fights_counter += 1
                    return Status.SUCCESSFULLY_STARTED_COMBAT
                else:
                    if map_coords != MapChanger.get_current_map_coords():
                        log.error("Map was accidentally changed during the attack.")
                        log.info("Attempting to change map back to original ...")
                        MapChanger.change_map(MapChanger.get_current_map_coords(), map_coords)
                        if MapChanger.has_loading_screen_passed():
                            log.info("Successfully changed map back to original!")
                            continue
                        log.error("Failed to change map back to original map.")
                        return Status.FAILED_TO_CHANGE_MAP_BACK_TO_ORIGINAL
                    elif self._is_char_in_lumberjack_workshop():
                        log.info("Character is in 'Lumberjack's Workshop'. Leaving ... ")
                        self._leave_lumberjacks_workshop()
                        if MapChanger.has_loading_screen_passed():
                            log.info("Successfully left 'Lumberjack's Workshop'.")
                            continue
                        log.error("Failed to leave 'Lumberjack's Workshop'.")
                        return Status.FAILED_TO_LEAVE_LUMBERJACK_WORKSHOP

        log.info(f"Map {map_coords} fully searched. Changing map ... ")
        MapChanger.change_map(map_coords, self._pathing_data[map_coords])
        if MapChanger.has_loading_screen_passed():
            return Status.MAP_FULLY_SEARCHED
        return Status.FAILED_TO_CHANGE_MAP

    def _get_monster_detection_data(self):
        image_folder_path = "src\\bot\\states\\out_of_combat\\sub_state\\hunting\\monster_images"
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

    def _get_join_sword_detection_data(self):
        paths = [
            "src\\bot\\states\\out_of_combat\\sub_state\\hunting\\images\\j_sword_ally_1.png",
            "src\\bot\\states\\out_of_combat\\sub_state\\hunting\\images\\j_sword_ally_2.png",
            "src\\bot\\states\\out_of_combat\\sub_state\\hunting\\images\\j_sword_ally_3.png",
            "src\\bot\\states\\out_of_combat\\sub_state\\hunting\\images\\j_sword_enemy.png",
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
        images_segment = self._monster_detection_data[0][segment_index]
        masks_segment = self._monster_detection_data[1][segment_index]
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

    def _is_attack_successful(self):
        start_time = perf_counter()
        while perf_counter() - start_time <= 6:
            if len(
                ImageDetection.find_images(
                    ScreenCapture.game_window(), 
                    ["src\\bot\\states\\out_of_combat\\sub_state\\hunting\\images\\cc_lit.png", 
                     "src\\bot\\states\\out_of_combat\\sub_state\\hunting\\images\\cc_dim.png"],
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

    def _is_char_in_lumberjack_workshop(self):
        return all ((
            pyag.pixelMatchesColor(49, 559, (0, 0, 0)),
            pyag.pixelMatchesColor(48, 137, (0, 0, 0)),
            pyag.pixelMatchesColor(782, 89, (0, 0, 0)),
            pyag.pixelMatchesColor(820, 380, (0, 0, 0)),
            pyag.pixelMatchesColor(731, 554, (0, 0, 0)),
        ))

    def _leave_lumberjacks_workshop(self):
        pyag.keyDown('e')
        pyag.moveTo(667, 507)
        pyag.click()
        pyag.keyUp('e')

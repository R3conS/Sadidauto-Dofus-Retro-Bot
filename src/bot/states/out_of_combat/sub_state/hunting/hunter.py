from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter, sleep
import os

import cv2
import pyautogui as pyag

from image_detection import ImageDetection
from src.bot.interfaces import Interfaces
from .map_data.getter import Getter as MapDataGetter
from screen_capture import ScreenCapture
from src.bot.map_changer.map_changer import MapChanger
from .status_enum import Status


class Hunter:

    def __init__(self, script: str, game_window_title: str):
        self.__game_window_title = game_window_title
        self.__consecutive_fights_counter = 0
        self.__check_pods_every_x_fights = 5
        # Map data
        map_data = MapDataGetter.get_data_object(script)
        self.__movement_data = map_data.get_movement_data()
        self.__map_type_data = map_data.get_map_type_data()
        self.__monster_detection_data = self.__get_monster_detection_data()
        self.__join_sword_detection_data = self.__get_join_sword_detection_data()

    def hunt(self):
        while True:
            if self.__consecutive_fights_counter >= self.__check_pods_every_x_fights:
                self.__consecutive_fights_counter = 0
                return Status.REACHED_CONSECUTIVE_FIGHTS_LIMIT

            map_coords = MapChanger.get_current_map_coords()
            log.info(f"Current map coordinates: {map_coords}")
            if not self.__are_map_coords_valid(map_coords, self.__movement_data):
                raise KeyError(f"Map coordinates {map_coords} are not in movement data!")

            map_type = self.__map_type_data[map_coords]

            if map_type == "traversable":
                if self.__handle_traversable_map(map_coords) == Status.FAILED_TO_TRAVERSE_MAP:
                    return Status.FAILED_TO_FINISH_HUNTING
                
            elif map_type == "fightable":
                log.info(f"Hunting on map: {map_coords} ... ")
                status = self.__handle_fightable_map(map_coords)
                if status == Status.SUCCESSFULLY_STARTED_COMBAT:
                    return Status.SUCCESSFULLY_FINISHED_HUNTING
                elif (
                    status == Status.FAILED_TO_CHANGE_MAP
                    or status == Status.FAILED_TO_LEAVE_LUMBERJACK_WORKSHOP
                ):
                    return Status.FAILED_TO_FINISH_HUNTING

    def __handle_traversable_map(self, map_coords):
        MapChanger.change_map(map_coords, self.__movement_data)
        if MapChanger.has_loading_screen_passed():
            return Status.SUCCESSFULLY_TRAVERSED_MAP
        log.info("Failed to detect loading screen after changing map.")
        return Status.FAILED_TO_TRAVERSE_MAP

    def __handle_fightable_map(self, map_coords):
        for segment_index in range(len(self.__monster_detection_data[0])):
            matches = self.__search_segment(segment_index, ScreenCapture.game_window())
            if len(matches) > 0:
                monster_x, monster_y = matches[0][0], matches[0][1]
                log.info(f"Found monster at {monster_x, monster_y}.")

                if self.__is_join_sword_on_pos(monster_x, monster_y):
                    log.info("Monster was attacked by someone else. Skipping ... ")
                    continue

                self.__attack(monster_x, monster_y)
                # Allow time for 'Right Click Menu' to open in case the attack 
                # click missed. Clicks can miss if the monster moves away.
                sleep(0.25) # Maybe increase this to 0.5?
                if Interfaces.is_right_click_menu_open():
                    log.info("Failed to attack monster because it moved away. Skipping ... ")
                    Interfaces.close_right_click_menu()
                    continue

                if self.__is_attack_successful():
                    self.__consecutive_fights_counter += 1
                    return Status.SUCCESSFULLY_STARTED_COMBAT
                else:
                    if map_coords != MapChanger.get_current_map_coords():
                        log.info("Map was changed during the attack.")
                        return Status.ACCIDENTALLY_CHANGED_MAP_DURING_ATTACK
                    elif self.__is_char_in_lumberjack_workshop():
                        log.info("Character is in 'Lumberjack's Workshop'. Leaving ... ")
                        self.__leave_lumberjacks_workshop()
                        if MapChanger.has_loading_screen_passed():
                            log.info("Successfully left 'Lumberjack's Workshop'.")
                            continue
                        log.info("Failed to leave 'Lumberjack's Workshop'.")
                        return Status.FAILED_TO_LEAVE_LUMBERJACK_WORKSHOP

        log.info(f"Map {map_coords} fully searched. Changing map ... ")
        MapChanger.change_map(map_coords, self.__movement_data)
        if MapChanger.has_loading_screen_passed():
            return Status.MAP_FULLY_SEARCHED
        return Status.FAILED_TO_CHANGE_MAP

    def __get_monster_detection_data(self):
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
            self.__segment_data(loaded_images, 4),
            self.__segment_data(ImageDetection.create_masks(loaded_images), 4)
        )

    def __get_join_sword_detection_data(self):
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

    def __segment_data(self, data: list, segment_size) -> list[list]:
        segments = []
        for i in range(0, len(data), segment_size):
            segments.append(data[i:i + segment_size])
        return segments

    def __search_segment(self, segment_index, haystack_image) -> list[tuple[int, int]]:
        images_segment = self.__monster_detection_data[0][segment_index]
        masks_segment = self.__monster_detection_data[1][segment_index]
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

    def __attack(self, monster_x, monster_y):
        log.info(f"Attacking monster at {monster_x, monster_y} ... ")
        pyag.moveTo(monster_x, monster_y)
        if "Dofus Retro" in self.__game_window_title:
            pyag.click(button="right")
        else: # For Abrak private server
            pyag.keyDown("shift")
            pyag.click()
            pyag.keyUp("shift")

    def __is_attack_successful(self):
        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if len(
                ImageDetection.find_images(
                    ScreenCapture.game_window(), 
                    ["src\\bot\\states\\out_of_combat\\sub_state\\hunting\\images\\cc_lit.png", 
                     "src\\bot\\states\\out_of_combat\\sub_state\\hunting\\images\\cc_dim.png"],
                )
            ) > 0:
                log.info("Attack successful.")
                return True
        log.info("Attack failed.")
        return False  

    def __is_join_sword_on_pos(self, x, y):
        haystack = ScreenCapture.around_pos((x, y), 65)
        for i, image in enumerate(self.__join_sword_detection_data[0]):
            result = ImageDetection.find_image(
                haystack,
                image,
                confidence=0.98,
                method=cv2.TM_CCORR_NORMED,
                mask=self.__join_sword_detection_data[1][i],
                remove_alpha_channels=True
            )
            if len(result) > 0:
                return True
        return False

    def __are_map_coords_valid(self, map_coords, movement_data):
        if map_coords in movement_data.keys():
            return True
        return False

    def __is_char_in_lumberjack_workshop(self):
        return all ((
            pyag.pixelMatchesColor(49, 559, (0, 0, 0)),
            pyag.pixelMatchesColor(48, 137, (0, 0, 0)),
            pyag.pixelMatchesColor(782, 89, (0, 0, 0)),
            pyag.pixelMatchesColor(820, 380, (0, 0, 0)),
            pyag.pixelMatchesColor(731, 554, (0, 0, 0)),
        ))

    def __leave_lumberjacks_workshop(self):
        pyag.keyDown('e')
        pyag.moveTo(667, 507)
        pyag.click()
        pyag.keyUp('e')

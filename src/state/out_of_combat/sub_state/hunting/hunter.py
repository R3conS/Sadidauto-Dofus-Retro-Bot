from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter, sleep
import os

import cv2
import pyautogui as pyag

import detection as dtc
from interfaces import Interfaces
from .map_data.getter import Getter as MapDataGetter
from src.map_changer.map_changer import MapChanger
import window_capture as wc


class Hunter:

    # ToDo: Fix __attack() method before fully commiting.

    def __init__(
            self, 
            finished_hunting_callback: callable, 
            script: str,
            game_window_title: str,
            game_window_size: tuple[int, int]
        ):
        self.__finished_hunting_callback = finished_hunting_callback
        self.__game_window_title = game_window_title
        self.__game_window_size = game_window_size
        self.fight_counter = 0
        # Map data
        map_data = MapDataGetter.get_data_object(script)
        self.__movement_data = map_data.get_movement_data()
        self.__map_type_data = map_data.get_map_type_data()
        self.__monster_detection_data = self.__get_monster_detection_data()
        self.__join_sword_detection_data = self.__get_join_sword_detection_data()

    def hunt(self):
        while True:
            map_coords = MapChanger.get_current_map_coords()
            log.info(f"Hunting on map: {map_coords}.")
            if not self.__are_map_coords_valid(map_coords, self.__movement_data):
                raise KeyError(f"Map coordinates {map_coords} are not in movement data!")

            map_type = self.__map_type_data[map_coords]

            if map_type == "traversable":
                status = self.__handle_traversable_map(map_coords)
                if status == "traversed_successfully":
                    continue
                elif status == "failed_to_handle":
                    # ToDo: Link to recovery state.
                    return
                
            elif map_type == "fightable":
                status = self.__handle_fightable_map(map_coords)
                if status == "started_combat":
                    # ToDo: Return control back to 'Out of Combat' state controller.
                    # self.__finished_hunting_callback()
                    return
                elif status == "accidentally_changed_map_during_attack":
                    continue
                elif status == "map_fully_searched":
                    continue
                elif status == "failed_to_handle":
                    # ToDo: Link to recovery state.
                    return

    def __handle_traversable_map(self, map_coords):
        MapChanger.change_map(map_coords, self.__movement_data)
        if MapChanger.has_loading_screen_passed():
            return "traversed_successfully"
        else:
            log.critical("Not implemented!")
            return "failed_to_handle"

    def __handle_fightable_map(self, map_coords):
        for segment_index in range(len(self.__monster_detection_data[0])):
            matches = self.__search_segment(segment_index, wc.WindowCapture.gamewindow_capture())
            if len(matches) > 0:
                monster_x, monster_y = matches[0][0], matches[0][1]
                
                log.info(f"Found monster at {monster_x, monster_y}.")
                if self.__is_join_sword_on_pos(monster_x, monster_y):
                    log.info("Monster was attacked by someone else. Skipping ... ")
                    continue
                self.__attack(monster_x, monster_y)
                # Allow time for 'Right Click Menu' to open in case the click missed.
                # Click can miss if monster moves from the coordinates.
                sleep(0.25)
                if Interfaces.is_right_click_menu_open():
                    log.info("Failed to attack monster because it moved away. Skipping ... ")
                    Interfaces.close_right_click_menu()
                    continue

                if self.__is_attack_successful():
                    self.fight_counter += 1
                    # ToDo: Return control back to 'Out of Combat' state controller.
                    # self.__finished_hunting_callback()
                    return "started_combat"
                else:
                    if map_coords != MapChanger.get_current_map_coords():
                        log.info("Map was changed during the attack.")
                        return "accidentally_changed_map_during_attack"
                    elif self.__is_char_in_lumberjack_workshop():
                        log.info("Character is in 'Lumberjack's Workshop'. Leaving ... ")
                        self.__leave_lumberjacks_workshop()
                        if MapChanger.has_loading_screen_passed():
                            log.info("Successfully left 'Lumberjack's Workshop'.")
                            continue
                        else:
                            return "failed_to_handle"

        log.info(f"Map {map_coords} fully searched. Changing map ... ")
        MapChanger.change_map(map_coords, self.__movement_data)
        if MapChanger.has_loading_screen_passed():
            return "map_fully_searched"
        return "failed_to_handle"

    def __get_monster_detection_data(self):
        image_folder_path = "src\\state\\out_of_combat\\sub_state\\hunting\\monster_images"
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
            self.__segment_data(dtc.Detection.create_masks(loaded_images), 4)
        )

    def __get_join_sword_detection_data(self):
        paths = [
            "src\\state\\out_of_combat\\sub_state\\hunting\\images\\j_sword_ally_1.png",
            "src\\state\\out_of_combat\\sub_state\\hunting\\images\\j_sword_ally_2.png",
            "src\\state\\out_of_combat\\sub_state\\hunting\\images\\j_sword_ally_3.png",
            "src\\state\\out_of_combat\\sub_state\\hunting\\images\\j_sword_enemy.png",
        ]
        read_images = []
        for path in paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Image path '{path}' does not exist.")
            read_images.append(cv2.imread(path, cv2.IMREAD_UNCHANGED))
        return read_images, dtc.Detection.create_masks(read_images)

    def __segment_data(self, data: list, segment_size) -> list[list]:
        segments = []
        for i in range(0, len(data), segment_size):
            segments.append(data[i:i + segment_size])
        return segments

    def __search_segment(self, segment_index, haystack_image) -> list[tuple[int, int]]:
        images_segment = self.__monster_detection_data[0][segment_index]
        masks_segment = self.__monster_detection_data[1][segment_index]
        matches = dtc.Detection.find_images(
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
                click_coords.append(dtc.Detection.get_rectangle_center_point(match))
        return click_coords

    def __attack(self, monster_x, monster_y):
        log.info(f"Attacking monster at {monster_x, monster_y} ... ")
        pyag.moveTo(monster_x, monster_y)
        if "Dofus Retro" in self.__game_window_title:
            pyag.click(button="right")
        else:
            pass
            # This is for Abrak server. Simply right clicking doesn't work (v1.42.3)
            # pyag.keyDown("shift")
            # pyag.click()
            # pyag.keyUp("shift")

    def __is_attack_successful(self):
        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if len(
                dtc.Detection.find_images(
                    wc.WindowCapture.gamewindow_capture(), 
                    ["src\\initializer\\cc_lit.png", "src\\initializer\\cc_dim.png"],
                )
            ) > 0:
                log.info("Attack successful.")
                return True
        log.info("Attack failed.")
        return False  

    def __is_join_sword_on_pos(self, x, y):
        haystack = wc.WindowCapture.area_around_mouse_capture(
            65, 
            (x, y),
            max_bottom_right_x=self.__game_window_size[0],
            max_bottom_right_y=self.__game_window_size[1]
        )
        for i, image in enumerate(self.__join_sword_detection_data[0]):
            result = dtc.Detection.find_image(
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

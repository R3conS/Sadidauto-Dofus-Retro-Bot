from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import time

import cv2
import pyautogui as pyag

from src.state.botstate_enum import BotState
import data
import detection as dtc
from interfaces import Interfaces
import window_capture as wc
from .map_data.getter import Getter as MapDataGetter
from src.map_changer import MapChanger



class Hunter:

    was_map_searched = False
    was_map_changed = False
    map_coords = None
    hunting_map_data = None
    banking_map_data = None
    fight_counter = 0 # True total fights counter is in fighting.py
    is_character_overloaded = False

    def __init__(self, finished_hunting_callback, script: str):
        self.__finished_hunting_callback = finished_hunting_callback
        self.__map_coords = None
        __map_data = MapDataGetter.get_data_object(script)
        self.__movement_data = __map_data.get_movement_data()
        self.__map_type_data = __map_data.get_map_type_data()
        self.__monster_data = dtc.Detection.generate_image_data(
            data.images.monster.AstrubForest.img_list,
            data.images.monster.AstrubForest.img_path
        )

    def hunt(self):
        while True:
            self.__map_coords = MapChanger.get_current_map_coords()
            if not self.__are_map_coords_valid(self.__map_coords, self.__movement_data):
                raise KeyError(f"Map coordinates {self.__map_coords} are not in movement data!")

            self.__map_type = self.__map_type_data[self.__map_coords]
            if self.__map_type == "traversable":
                MapChanger.change_map(self.__map_coords, self.__movement_data)
                if MapChanger.has_loading_screen_passed():
                    continue
                else:
                    # ToDo: Link to recovery state.
                    log.critical("Not implemented!")
            elif self.__map_type == "fightable":
                pass

    def __are_map_coords_valid(self, map_coords, movement_data):
        if map_coords in movement_data.keys():
            return True
        return False

    def search(self):
        segmented_data = self.__segment_monster_data(list(self.__monster_data.keys()), 14)
        monster_data = dtc.Detection.generate_image_data(
            data.images.monster.AstrubForest.img_list,
            data.images.monster.AstrubForest.img_path
        )
        for segment_i, segment_data in segmented_data.items():
            log.info(f"Searching segment: {segment_i} ... ")
            _, monster_coords = self.__search_segment(monster_data, segment_data)
            print(monster_coords)

    def attack(self, monster_coords: list[tuple[int, int]]):
        pyag.moveTo(monster_coords[0][0], monster_coords[0][1])
        # ToDo: Change this to work with official server.
        pyag.click()

    def __search_segment(self, monster_data, segment_data):
        screenshot = wc.WindowCapture.gamewindow_capture()
        obj_rects, obj_coords = dtc.Detection.detect_objects_with_masks(
                monster_data,
                segment_data,
                screenshot,
            )

        if len(obj_coords) > 0:
            log.info(f"Monsters found at: {obj_coords}!")
            return obj_rects, obj_coords

    def __hunt_old(self):
        log.info(f"Hunting on map ({self.map_coords}) ... ")

        # Chunks of monsters to search through.
        chunks = self.__segment_monster_data(list(self.__monster_data.keys()), 14)
        # Stores chunks of monsters on which character failed an attack
        # >= 'fails_allowed' times.
        forbidden_chunks = []
        # Counts how many times an attack on monster was failed.
        fails_total = 0
        # How many failed attempts to attack a monster on a specific
        # 'chunk' are allowed.
        fails_allowed = 3
        # How many mmonster detections from a single chunk are allowed 
        # before considering the whole detection list 'False'.
        allowed_detections = 9
        # Loop control variables.
        start_time = time.time()
        timeout = 90

        while time.time() - start_time < timeout:
            for chunk_number, chunk in chunks.items():
                if chunk_number in forbidden_chunks:
                    if len(chunks) == len(forbidden_chunks):
                        self.__controller.set_was_map_searched(True)
                        self.__state = BotState.CONTROLLER
                        return self.__state
                    else:
                        continue

                log.debug(f"Searching chunk: {chunk_number} ... ")
                _, obj_coords = self.__search_old(self.__monster_data, chunk)

                if len(obj_coords) > allowed_detections:
                    log.debug(f"Too many detections, most likely false ... ")
                    forbidden_chunks.append(chunk_number)
                    continue

                if len(obj_coords) > 0:
                    attack = self.__attack_old(obj_coords)
                    if attack == "success":
                        self.__state = BotState.PREPARING
                        return self.__state
                    elif attack == "map_change":
                        self.__state = BotState.CONTROLLER
                        return self.__state
                    elif attack == "fail":
                        forbidden_chunks.append(chunk_number)
                        break
                    elif attack == "sword" or attack == "right_click_menu":
                        fails_total += 1
                        if fails_total >= fails_allowed:
                            log.debug("Too many failed attack attemps on chunk"
                                      f" {chunk_number}!")
                            log.debug(f"Adding {chunk_number} to forbidden "
                                      "chunks!")
                            forbidden_chunks.append(chunk_number)
                            fails_total = 0
                        break
                # If all chunks have been searched through.
                if chunk_number + 1 == len(chunks.keys()):
                    log.info(f"Map ({self.map_coords}) is clear!")
                    self.__controller.set_was_map_searched(True)
                    self.__state = BotState.CONTROLLER
                    return self.__state
        else:
            log.error(f"Timed out in 'hunting()'!")
            if self.__controller.moving.emergency_teleport():
                self.__state = BotState.CONTROLLER
                return self.__state

    def __attack_old(self, monster_coords):
        wait_after_attacking = 9
        attempts_allowed = 2
        attempts_total = 0

        if len(monster_coords) < attempts_allowed:
            attempts_allowed = len(monster_coords)

        for i in range(0, attempts_allowed):

            x, y = monster_coords[i]


            # Taking a screenshot that is used later to determine
            # whether map was accidentally changed during attack.
            scs_before_attack = self.__controller.moving.screenshot_minimap()

            # Checking if monster was attacked by other player.
            if self.__is_join_sword_on_pos((x, y)):
                log.info(f"Failed to attack monster at {x, y} because it was "
                         "attacked by someone else!")
                return "sword"

            log.info(f"Attacking monster at: {x, y} ... ")
            pyag.moveTo(x, y)
            # pyag.click(button="right")
            pyag.click(button="left")

            attack_time = time.time()
            while time.time() - attack_time < wait_after_attacking:

                screenshot = wc.WindowCapture.gamewindow_capture()
                cc_icon = dtc.Detection.find(
                        screenshot,
                        data.images.Status.preparing_sv_1
                    )
                ready_button = dtc.Detection.find(
                        screenshot,
                        data.images.Status.preparing_sv_2
                    )
                
                if len(cc_icon) > 0 and len(ready_button) > 0:
                    log.info(f"Successfully attacked monster at: {x, y}!")
                    return "success"

            else:

                log.info(f"Failed to attack monster at: {x, y}!")
                attempts_total += 1

                if self.__accidental_map_change(scs_before_attack):
                    return "map_change"

                if attempts_allowed == attempts_total:
                    return "fail"

    def __accidental_map_change(self, sc_before_attack):
        """
        Check if map was changed accidentally during an attack.

        Parameters
        ----------
        sc_before_attack : np.ndarray
            Screenshot of minimap before attacking.

        Returns
        ----------
        True : bool
            If map was changed.
        
        """
        sc_after_attack = self.__controller.moving.screenshot_minimap()
        rects = dtc.Detection.find(sc_before_attack,
                                   sc_after_attack,
                                   threshold=0.98)
        if len(rects) <= 0:
            log.info("Map was changed accidentally during an attack!")
            self.__controller.was_map_changed = True
            return True

    @staticmethod
    def __segment_monster_data(image_list, segment_size):
        """Split monster image list into equally sized segments."""
        total_images = len(image_list)
        chunkated_data = []
        for i in range(0, total_images, segment_size):
            chunk = image_list[i:i+segment_size]
            chunkated_data.append(chunk)
        return {k: v for k, v in enumerate(chunkated_data)}

    @staticmethod
    def __search_old(image_data, image_list):
        screenshot = wc.WindowCapture.gamewindow_capture()
        obj_rects, obj_coords = dtc.Detection.detect_objects_with_masks(
                image_data,
                image_list,
                screenshot,
            )

        if len(obj_coords) > 0:
            log.info(f"Monsters found at: {obj_coords}!")
            return obj_rects, obj_coords

        return obj_rects, obj_coords

    @staticmethod
    def __is_join_sword_on_pos(coordinates):
        """
        Check if 'Join' sword is around `coordinates`.

        Parameters
        ---------- 
        coordinates : Tuple[int, int]
            (x, y) coordinate to search around.
        
        Returns
        ----------
        coords : list[Tuple[int, int]]
            `list` of `tuple` of (x, y) coordinates where sword was
            found.
        coords : list
            Empty `list` if no sword was found.

        """
        path = data.images.Combat.path
        swords = [data.images.Combat.a_sword, data.images.Combat.m_sword]
        sc = wc.WindowCapture.area_around_mouse_capture(60, coordinates)
        img_data = dtc.Detection.generate_image_data(swords, path)
        _, coords = dtc.Detection.detect_objects_with_masks(
                img_data,
                swords,
                sc,
                threshold=0.958
            )
        return len(coords) > 0

    @staticmethod
    def __detect_lumberjack_ws_interior():
        """Detect if character is inside lumberjack's workshop."""
        color = (0, 0, 0)
        coordinates = [(49, 559), (48, 137), (782, 89), (820, 380), (731, 554)]

        pixels = []
        for coord in coordinates:
            px = pyag.pixelMatchesColor(coord[0], coord[1], color)
            pixels.append(px)

        if all(pixels):
            log.info("Character is inside 'Lumberjack's Workshop'!")
            return True
        else:
            return False

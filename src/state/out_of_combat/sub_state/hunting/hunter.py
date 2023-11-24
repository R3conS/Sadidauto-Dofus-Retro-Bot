from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import time

import pyautogui as pyag

from src.state.botstate_enum import BotState
import data
import detection as dtc
from interfaces import Interfaces
import window_capture as wc
from .map_data.getter import Getter as MapDataGetter


class Hunter:

    map_coords = None
    __state = None

    def __init__(self, finished_hunting_callback, script: str):
        self.finished_hunting_callback = finished_hunting_callback
        __map_data = MapDataGetter.get_data_object(script)
        self.__movement_data = __map_data.get_movement_data()
        self.__map_type_data = __map_data.get_map_type_data()
        self.__monster_data = dtc.Detection.generate_image_data(
            data.images.monster.AstrubForest.img_list,
            data.images.monster.AstrubForest.img_path
        )

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

    def hunt(self):
        log.info(f"Hunting on map ({self.map_coords}) ... ")

        # Chunks of monsters to search through.
        chunks = self.__chunkate_data(list(self.__monster_data.keys()), 14)
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
                _, obj_coords = self.__search(self.__monster_data, chunk)

                if len(obj_coords) > allowed_detections:
                    log.debug(f"Too many detections, most likely false ... ")
                    forbidden_chunks.append(chunk_number)
                    continue

                if len(obj_coords) > 0:

                    attack = self.__attack(obj_coords)

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

    def __attack(self, monster_coords):
        """
        Attack monsters.

        Parameters
        ----------
        monster_coords : list[Tuple[int, int]]
            Monster coordinates.
        
        Returns
        ----------
        True : bool
            If monster was attacked successfully.
        False : bool
            If failed to attack monster `attempts_allowed` times.
        
        """
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
            if self.__check_sword((x, y)):
                log.info(f"Failed to attack monster at {x, y} because it was "
                         "attacked by someone else!")
                return "sword"

            log.info(f"Attacking monster at: {x, y} ... ")
            pyag.moveTo(x, y)
            # pyag.click(button="right")
            pyag.click(button="left")

            # Checking if monster moved.
            if self.__check_right_click_menu():
                log.info(f"Failed to attack monster at {x, y} because it "
                         "moved!")
                return "right_click_menu"
            
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
    def __chunkate_data(image_list, chunk_size):
        """
        Split monster image list into equally sized chunks.
        
        Parameters
        ----------
        image_list : list[str]
            `list` of `str` containing names of image files.
        chunk_size : int
            Amount of images to put in a chunk.

        Returns
        ----------
        chunkated_data : dict[int: list[str]]
            `image_list` split into equal `chunk_size` chunks. Last
            chunk won't have `chunk_size` images if len(`image_list`) %
            `chunk_size` != 0.

        """
        total_images = len(image_list)

        chunkated_data = []
        for i in range(0, total_images, chunk_size):
            chunk = image_list[i:i+chunk_size]
            chunkated_data.append(chunk)

        chunkated_data = {k: v for k, v in enumerate(chunkated_data)}

        return chunkated_data

    @staticmethod
    def __search(image_data, image_list):
        """
        Search for monsters.
        
        Parameters
        ----------
        image_data : dict[str: Tuple[np.ndarray, np.ndarray]]
            Dictionary containing image information. Can be generated by
            `generate_image_data()` method.
        image_list : list[str]
            `list` of images to search for. These images are used as
            keys to access data in `image_data`.

        Returns
        ----------
        obj_rects : list[list[int]]
            2D `list` containing [[topLeft_x, topLeft_y, width, height]] 
            of bounding box.
        obj_coords : list[Tuple[int, int]]
            `list` of `tuple` containing [(x, y)] coordinates.
        obj_rects : tuple
            Empty `tuple` if no matches found.
        obj_coords : list
            Empty `list` if no matches found.

        """
        # MapChanger mouse of the screen so it doesn't hightlight mobs
        # by accident causing them to be undetectable.
        Interfaces.close_right_click_menu()

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
    def __check_right_click_menu():
        """Check if right click menu is open."""
        # Allowing the menu to appear before taking a screnshot.
        time.sleep(0.5)
        sc = wc.WindowCapture.gamewindow_capture()
        rects = dtc.Detection.find(sc, 
                                   data.images.Interface.right_click_menu,
                                   threshold=0.6)
        if len(rects) > 0:
            return True
        else:
            return False

    @staticmethod
    def __check_sword(coordinates):
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
        return coords

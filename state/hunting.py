"""Logic related to 'HUNTING' bot state."""

from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True)

import time

import pyautogui as pyag

from .botstate_enum import BotState
import data
import detection as dtc
import pop_up as pu
import state
import window_capture as wc


class Hunting:
    """Holds various 'HUNTING' state methods."""

    # Public class attributes.
    map_coords = None
    data_monsters = None

    # Private class attributes.
    __state = None

    @classmethod
    def hunting(cls):
        """'HUNTING' state logic."""
        log.info(f"Hunting on map ({cls.map_coords}) ... ")

        chunks = cls.__chunkate_data(list(cls.data_monsters.keys()), 4)
        start_time = time.time()
        timeout = 90

        while time.time() - start_time < timeout:

            for chunk_number, chunk in chunks.items():

                log.debug(f"Searching chunk: {chunk_number} ... ")
                _, obj_coords = cls.__search(cls.data_monsters, chunk)

                if len(obj_coords) > 0:

                    attack = cls.__attack(obj_coords)

                    if attack == "success":
                        cls.__state = BotState.PREPARING
                        return cls.__state

                    elif attack == "map_change":
                        cls.__state = BotState.CONTROLLER
                        return cls.__state

                    elif attack == "sword":
                        log.debug(f"Breaking out of search loop to start from "
                                  "chunk 0 ... ")
                        break

                    elif attack == "right_click_menu":
                        log.debug(f"Breaking out of search loop to start from "
                                  "chunk 0 ... ")
                        break

                # If all chunks have been searched through.
                if chunk_number + 1 == len(chunks.keys()):
                    log.info(f"Map ({cls.map_coords}) is clear!")
                    state.Controller.map_searched = True
                    cls.__state = BotState.CONTROLLER
                    return cls.__state

        else:
            log.error(f"Timed out in 'hunting()'!")
            if state.Moving.emergency_teleport():
                cls.__state = BotState.CONTROLLER
                return cls.__state

    @classmethod
    def __attack(cls, monster_coords):
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
        wait_after_attacking = 6
        attempts_allowed = 3
        attempts_total = 0

        if len(monster_coords) < attempts_allowed:
            attempts_allowed = len(monster_coords)

        for i in range(0, attempts_allowed):

            pu.PopUp.deal()
            scs_before_attack = state.Moving.screenshot_minimap()

            x, y = monster_coords[i]

            # Checking if monster was attacked by other player.
            if cls.__check_sword((x, y)):
                log.info(f"Failed to attack monster at {x, y} because it was "
                         "attacked by someone else!")
                return "sword"

            log.info(f"Attacking monster at: {x, y} ... ")
            pyag.moveTo(x, y, duration=0.15)
            time.sleep(0.25)
            pyag.click(button="right")

            # Checking if monster moved.
            if cls.__check_right_click_menu():
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

                if cls.__accidental_map_change(scs_before_attack):
                    return "map_change"

                if (attempts_allowed == attempts_total):
                    return "fail"

    @classmethod
    def __accidental_map_change(cls, sc_before_attack):
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
        sc_after_attack = state.Moving.screenshot_minimap()
        rects = dtc.Detection.find(sc_before_attack,
                                   sc_after_attack,
                                   threshold=0.98)
        if len(rects) <= 0:
            log.info("Map was changed accidentally during an attack!")
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
        # Moving mouse of the screen so it doesn't hightlight mobs
        # by accident causing them to be undetectable.
        pu.PopUp.close_right_click_menu()

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

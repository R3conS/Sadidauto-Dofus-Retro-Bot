from src.logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from collections import deque
import os
from time import perf_counter
import re

import cv2
import pyautogui as pyag

from image_detection import ImageDetection
from screen_capture import ScreenCapture
from src.utilities import load_image
from ._map_data import DATA as MAP_DATA


class MapChanger:

    IMAGE_DIR_PATH = "src\\bot\\_map_changer\\_images"
    MAP_IMAGE_DATA = {}
    for image_name in [name for name in os.listdir(IMAGE_DIR_PATH) if name.endswith(".png")]:
        MAP_IMAGE_DATA[image_name.replace(".png", "")] = load_image(IMAGE_DIR_PATH, image_name)
    MAP_CHANGE_DATA = MAP_DATA
    MAP_IMAGE_AREA = (487, 655, 78, 52)

    @classmethod
    def get_current_map_coords(cls):
        current_map_image = cls._screenshot_map_area()
        for map_coords, map_image in cls.MAP_IMAGE_DATA.items():
            result = ImageDetection.find_image(
                haystack=map_image,
                needle=current_map_image,
                confidence=0.99,
                method=cv2.TM_SQDIFF_NORMED,
                remove_alpha_channels=True,
            )
            if len(result) > 0:
                match = re.search(r'-?\d{1,2},-?\d{1,2}', map_coords)
                if match:
                    return match.group()
        raise ValueError(f"Failed to find current map coords. Perhaps the map image is missing?")

    @classmethod
    def change_map(cls, from_map: str, to_map: str):
        log.info(f"Changing map from '{from_map}' to '{to_map}' ... ")
        if from_map not in cls.MAP_CHANGE_DATA:
            raise ValueError(f"Data for map coords '{from_map}' not found in MAP_DATA.")
        if to_map not in cls.MAP_CHANGE_DATA[from_map]:
            raise ValueError(f"Map change (sun) coords for map '{to_map}' not found in '{from_map}' map's data.")
        if cls.MAP_CHANGE_DATA[from_map][to_map] is None:
            raise ValueError(f"Impossible to change map from '{from_map}' to '{to_map}' because there is no map change (sun) icon in that direction.")
        
        sun_x, sun_y = cls.MAP_CHANGE_DATA[from_map][to_map]
        pyag.keyDown("e")
        pyag.moveTo(sun_x, sun_y)
        pyag.click()
        pyag.keyUp("e")

    @staticmethod
    def has_loading_screen_passed():
        log.info(f"Waiting for loading screen ... ")
        start_time = perf_counter()
        while perf_counter() - start_time <= 10:
            if MapChanger._is_loading_screen_visible():
                log.info(f"Loading screen detected ... ")
                break
        else:
            log.error(f"Failed to detect loading screen.")
            return False
        
        start_time = perf_counter()
        while perf_counter() - start_time <= 10:
            if not MapChanger._is_loading_screen_visible():
                log.info(f"Loading screen finished.")
                return True
        else:
            log.error(f"Failed to detect end of loading screen.")
            return False

    @classmethod
    def get_shortest_path(cls, start, end) -> dict[str, str]: # {from_map: to_map}
        if start not in cls.MAP_CHANGE_DATA:
            raise ValueError(f"Impossible to generate path from '{start}' to '{end}' because '{start}' is not in MAP_DATA.")
        if end not in cls.MAP_CHANGE_DATA:
            raise ValueError(f"Impossible to generate path from '{start}' to '{end}' because '{end}' is not in MAP_DATA.")
        if start == end:
            raise ValueError(f"Impossible to generate path from '{start}' to '{end}' because they are the same.")

        queue = deque([(start, [start])])
        visited = set([start])
        while queue:
            node, path = queue.popleft()
            for next_node in cls.MAP_CHANGE_DATA[node]:
                if next_node == end:
                    path += [next_node]
                    return {path[i]: path[i + 1] for i in range(len(path) - 1)}
                if next_node in cls.MAP_CHANGE_DATA and next_node not in visited:
                    queue.append((next_node, path + [next_node]))
                    visited.add(next_node)
        
        raise Exception(f"Impossible to generate path from '{start}' to '{end}' because there are no maps conecting them.")

    @staticmethod
    def _is_loading_screen_visible():
        return all((
            pyag.pixelMatchesColor(529, 491, (0, 0, 0)),
            pyag.pixelMatchesColor(531, 429, (0, 0, 0)),
            pyag.pixelMatchesColor(364, 419, (0, 0, 0)),
            pyag.pixelMatchesColor(691, 424, (0, 0, 0))
        ))

    @classmethod
    def _screenshot_map_area(cls):
        return ScreenCapture.custom_area(cls.MAP_IMAGE_AREA)

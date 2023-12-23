from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import os
from time import perf_counter, sleep

import cv2
import pyautogui as pyag

from image_detection import ImageDetection
from screen_capture import ScreenCapture
from src.utilities import load_image


class MapChanger:

    _image_dir_path = "src\\bot\\map_changer\\map_images"
    map_data = {}
    for image_name in [name for name in os.listdir(_image_dir_path) if name.endswith(".png")]:
        map_data[image_name.replace(".png", "")] = load_image(_image_dir_path, image_name)

    @classmethod
    def get_current_map_coords(cls):
        current_map_image = ScreenCapture.custom_area((487, 655, 78, 52))
        for map_coords, map_image in cls.map_data.items():
            result = ImageDetection.find_image(
                haystack=map_image,
                needle=current_map_image,
                confidence=0.99,
                method=cv2.TM_SQDIFF_NORMED,
                remove_alpha_channels=True,
            )
            if len(result) > 0:
                return map_coords
        raise ValueError(f"Failed to find current map coords. Perhaps the map image is missing?")

    @staticmethod
    def change_map(map_coords: str, map_data: dict[str, tuple[int, int]]):
        log.info(f"Changing map ... ")
        sun_x, sun_y = map_data[map_coords]
        pyag.keyDown("e")
        pyag.moveTo(sun_x, sun_y)
        # When moving downwards need to wait for health bar to disappear
        # before clicking.
        if sun_y >= 560: 
            sleep(0.5)
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

    @staticmethod
    def _is_loading_screen_visible():
        return all((
            pyag.pixelMatchesColor(529, 491, (0, 0, 0)),
            pyag.pixelMatchesColor(531, 429, (0, 0, 0)),
            pyag.pixelMatchesColor(364, 419, (0, 0, 0)),
            pyag.pixelMatchesColor(691, 424, (0, 0, 0))
        ))

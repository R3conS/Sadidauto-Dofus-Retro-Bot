from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import os
from time import perf_counter, sleep

import cv2
import numpy as np
import pyautogui as pyag

import detection as dtc
import window_capture as wc


def _load_map_image_data() -> dict[str, np.ndarray]:
    folder_path = "src\\map_changer\\map_images"
    image_names = [name for name in os.listdir(folder_path) if name.endswith(".png")]
    loaded_images = {}
    for map_image_name in image_names:
        map_image_path = os.path.join(folder_path, map_image_name)
        loaded_images[map_image_name.replace(".png", "")] = cv2.imread(map_image_path, cv2.IMREAD_UNCHANGED)
    return loaded_images


class MapChanger:

    map_data = _load_map_image_data()

    @classmethod
    def get_current_map_coords(cls):
        current_map_image = wc.WindowCapture.custom_area_capture(
            capture_region=(487, 655, 78, 52),
        )
        for map_coords, map_image in cls.map_data.items():
            result = dtc.Detection.find_image(
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
        if sun_y < 560: 
            sleep(0.5)
        pyag.click()
        pyag.keyUp("e")

    @staticmethod
    def has_loading_screen_passed():
        log.info(f"Waiting for loading screen ... ")
        start_time = perf_counter()
        while perf_counter() - start_time <= 10:
            if MapChanger.__is_loading_screen_visible():
                log.info(f"Loading screen detected ... ")
                break
        else:
            log.error(f"Failed to detect loading screen.")
            return False
        
        start_time = perf_counter()
        while perf_counter() - start_time <= 10:
            if not MapChanger.__is_loading_screen_visible():
                log.info(f"Loading screen finished.")
                return True
        else:
            log.error(f"Failed to detect end of loading screen.")
            return False

    @staticmethod
    def __is_loading_screen_visible():
        return all((
            pyag.pixelMatchesColor(529, 491, (0, 0, 0)),
            pyag.pixelMatchesColor(531, 429, (0, 0, 0)),
            pyag.pixelMatchesColor(364, 419, (0, 0, 0)),
            pyag.pixelMatchesColor(691, 424, (0, 0, 0))
        ))


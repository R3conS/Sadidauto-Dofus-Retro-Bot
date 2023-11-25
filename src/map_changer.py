from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import os
from time import perf_counter, sleep

import cv2
import pyautogui as pyag

import detection as dtc
import window_capture as wc


class MapChanger:

    @staticmethod
    def get_current_map_coords():
        log.info(f"Getting current map coordinates ... ")

        MapChanger.__trigger_map_tooltip()
        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if MapChanger.__is_map_tooltip_visible():
                break
        else:
            log.error(f"Failed to detect map tooltip!")
            # ToDo: Link to recovery state.
            os._exit(1)

        screenshot = wc.WindowCapture.custom_area_capture(
                capture_region=(525, 650, 45, 30),
                conversion_code=cv2.COLOR_RGB2GRAY,
                interpolation_flag=cv2.INTER_LINEAR,
                scale_width=160,
                scale_height=200
            )
        try:
            coords = dtc.Detection.get_text_from_image(screenshot)[0]
            coords = coords.replace(".", ",")
            coords = coords.replace(" ", "")
            # Inserting ',' if it wasn't detected before second '-'.
            if "-" in coords:
                index = coords.rfind("-")
                if index != 0:
                    if coords[index-1].isdigit():
                        coords = coords[:index] + "," + coords[index:]
            log.info(f"Current map coordinates: {coords}.")
            return coords
        except IndexError:
            log.error(f"Failed to read map coordinates from map tooltip!")
            os._exit(1)

    @staticmethod
    def change_map(map_coords: str, map_data: dict[str, tuple[int, int]]):
        log.info(f"Changing map to: {map_coords} ... ")
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
                log.info(f"Loading screen detected.")
                break
        else:
            log.error(f"Failed to detect loading screen!")
            return False
        
        start_time = perf_counter()
        while perf_counter() - start_time <= 10:
            if not MapChanger.__is_loading_screen_visible():
                log.info(f"Loading screen finished.")
                return True
        else:
            log.error(f"Failed to detect end of loading screen!")
            return False

    @staticmethod
    def __trigger_map_tooltip():
        log.info(f"Triggering map tooltip to appear ... ")
        pyag.moveTo(517, 680)

    @staticmethod
    def __is_map_tooltip_visible():
        tooltip_area = wc.WindowCapture.custom_area_capture(
            capture_region=(520, 650, 50, 35),
            conversion_code=cv2.COLOR_RGB2GRAY,
            interpolation_flag=cv2.INTER_LINEAR,
            scale_width=160,
            scale_height=200
        )
        _, tooltip_area = cv2.threshold(tooltip_area, 90, 255, cv2.THRESH_BINARY)
        tooltip_area = cv2.bitwise_not(tooltip_area)
        contours, _ = cv2.findContours(tooltip_area, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            _, _, w, h = cv2.boundingRect(contour)
            if w > 20 and h > 20:
                log.info(f"Map tooltip is visible!")
                return True
        return False

    @staticmethod
    def __is_loading_screen_visible():
        return all((
            pyag.pixelMatchesColor(529, 491, (0, 0, 0)),
            pyag.pixelMatchesColor(531, 429, (0, 0, 0)),
            pyag.pixelMatchesColor(364, 419, (0, 0, 0)),
            pyag.pixelMatchesColor(691, 424, (0, 0, 0))
        ))


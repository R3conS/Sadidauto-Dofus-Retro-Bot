from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import os
from time import perf_counter

import cv2
import numpy as np
import pyautogui as pyag

from .status_enum import Status
from .map_data.getter import Getter as MapDataGetter
from src.map_changer.map_changer import MapChanger
from src.screen_capture import ScreenCapture
from src.image_detection import ImageDetection


def _load_image(image_folder_path: str, image_name: str):
    image_path = os.path.join(image_folder_path, image_name)
    if not os.path.exists(image_path) and not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image '{image_name}' not found in '{image_folder_path}'.")
    return cv2.imread(image_path, cv2.IMREAD_UNCHANGED)


class Preparer:

    image_folder_path = "src\\state\\in_combat\\sub_state\\preparing\\images"
    loading_icon_image = _load_image(image_folder_path, "loading_icon.png")
    loading_icon_image_mask = ImageDetection.create_mask(loading_icon_image)

    RED = "red"
    BLUE = "blue"

    def __init__(self, script: str):
        self.__starting_cell_data = MapDataGetter.get_data_object(script).get_starting_cells()
        self.__dummy_cell_data = MapDataGetter.get_data_object(script).get_dummy_cells()

    def prepare(self):
        map_coords = MapChanger.get_current_map_coords()
        
        dummy_cell_color = None
        result = self.handle_dummy_cells(map_coords)
        if result == Status.FAILED_TO_MOVE_TO_DUMMY_CELLS:
            return Status.FAILED_TO_PREPARE
        else:
            if isinstance(result, str):
                dummy_cell_color = result
        
        result = self.handle_starting_cells(map_coords, dummy_cell_color)
        if result == Status.FAILED_TO_MOVE_TO_STARTING_CELLS:
            return Status.FAILED_TO_PREPARE

    def handle_dummy_cells(self, map_coords: str):
        log.info(f"Checking for dummy cells on map: {map_coords} ... ")
        red_dummy_cells = self.get_free_dummy_cells(self.RED, map_coords)
        blue_dummy_cells = self.get_free_dummy_cells(self.BLUE, map_coords)
        if len(red_dummy_cells) == 0 and len(blue_dummy_cells) == 0:
            log.info("No dummy cells found on this map.")
            return Status.NO_DUMMY_CELLS_ON_THIS_MAP
        
        log.info("Dummy cells found. Attempting to move ... ")

        for cell_coords in red_dummy_cells:
            status = self.move_char_to_cell(*cell_coords)
            if status == Status.SUCCESSFULLY_MOVED_TO_CELL:
                log.info(f"Successfully moved to red side dummy cell: {cell_coords}.")
                return self.RED
        for cell_coords in blue_dummy_cells:
            status = self.move_char_to_cell(*cell_coords)
            if status == Status.SUCCESSFULLY_MOVED_TO_CELL:
                log.info(f"Successfully moved to blue side dummy cell: {cell_coords}.")
                return self.BLUE
        
        log.info("Failed to move to dummy cells.")
        return Status.FAILED_TO_MOVE_TO_DUMMY_CELLS

    def handle_starting_cells(self, map_coords: str, dummy_cell_color: str = None):
        log.info(f"Attempting to move to a starting cell on map: {map_coords} ... ")
        if dummy_cell_color is not None:
            starting_cells = self.get_free_starting_cells(dummy_cell_color, map_coords)
        else:
            red_starting_cells = self.get_free_starting_cells(self.RED, map_coords)
            blue_starting_cells = self.get_free_starting_cells(self.BLUE, map_coords)
            starting_cells = red_starting_cells + blue_starting_cells

        for cell_coords in starting_cells:
            result = self.move_char_to_cell(*cell_coords)
            if result == Status.SUCCESSFULLY_MOVED_TO_CELL:
                if dummy_cell_color is not None:
                    log.info(f"Successfully moved to {dummy_cell_color} side starting cell: {cell_coords}.")
                else:
                    if cell_coords in red_starting_cells:
                        log.info(f"Successfully moved to red side starting cell: {cell_coords}.")
                    else:
                        log.info(f"Successfully moved to blue side starting cell: {cell_coords}.")
                return Status.SUCCESSFULLY_MOVED_TO_CELL
        
        log.info("Failed to move to a starting cell.")
        return Status.FAILED_TO_MOVE_TO_STARTING_CELLS

    def move_char_to_cell(self, cell_x, cell_y):
        screenshot_before_clicking_cell = self.screenshot_cell_area(cell_x, cell_y)
        self.click_cell(cell_x, cell_y)
        if self.did_char_move(cell_x, cell_y, screenshot_before_clicking_cell):
            return Status.SUCCESSFULLY_MOVED_TO_CELL
        return Status.FAILED_TO_MOVE_TO_CELL

    def get_dummy_cells(self, map_coords: str, color: str):
        if color not in [self.RED, self.BLUE]:
            raise ValueError(f"Invalid cell color: '{color}'.")
        for map, cell_data in self.__dummy_cell_data.items():
            if map == map_coords:
                return cell_data[color]

    def get_free_dummy_cells(self, map_coords: str, color: str):
        free_cells = []
        for cell_coords in self.get_dummy_cells(color, map_coords):
            game_window_screenshot = pyag.screenshot(region=ScreenCapture.game_window_area)
            if self.is_cell_free(*cell_coords, game_window_screenshot):
                free_cells.append(cell_coords)
        return free_cells

    def get_starting_cells(self, map_coords: str, color: str):
        if color not in [self.RED, self.BLUE]:
            raise ValueError(f"Invalid cell color: '{color}'.")
        for map, cell_data in self.__starting_cell_data.items():
            if map == map_coords:
                return cell_data[color]

    def get_free_starting_cells(self, map_coords: str, color: str):
        free_cells = []
        for cell_coords in self.get_starting_cells(color, map_coords):
            game_window_screenshot = pyag.screenshot(region=ScreenCapture.game_window_area)
            if self.is_cell_free(*cell_coords, game_window_screenshot):
                free_cells.append(cell_coords)
        return free_cells

    @staticmethod
    def is_cell_free(cell_x, cell_y, game_window_screenshot=None):
        if game_window_screenshot is None:
            game_window_screenshot = pyag.screenshot(region=ScreenCapture.game_window_area)
        for color in [(255, 0, 0), (154, 0, 0), (0, 0, 255), (0, 0, 154)]:
            if game_window_screenshot.getpixel((cell_x, cell_y)) == color:
                return True
        return False

    @staticmethod
    def are_images_same(before, after):
        return len(
            ImageDetection.find_image(
                haystack=before,
                needle=after,
                method=cv2.TM_CCOEFF_NORMED,
                confidence=0.99
            )
        ) > 0

    @staticmethod
    def screenshot_cell_area(cell_x, cell_y):
        return ScreenCapture.around_pos((cell_x, cell_y), 30)

    @staticmethod
    def click_cell(cell_x, cell_y):
        pyag.moveTo(cell_x, cell_y)
        pyag.click()

    @classmethod
    def did_char_move(cls, cell_x, cell_y, cell_area_before_moving: np.ndarray):
        start_time = perf_counter()
        while perf_counter() - start_time <= 0.5:
            if not cls.are_images_same(
                cell_area_before_moving, 
                cls.screenshot_cell_area(cell_x, cell_y)
            ):
                return True
        return False

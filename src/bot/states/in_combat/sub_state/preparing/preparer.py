from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import os
from time import perf_counter

import cv2
import numpy as np
import pyautogui as pyag
from PIL import Image

from src.utilities import move_mouse_off_game_area
from .status_enum import Status
from .map_data.getter import Getter as MapDataGetter
from src.bot.map_changer.map_changer import MapChanger
from src.screen_capture import ScreenCapture
from src.image_detection import ImageDetection


def _load_image(image_folder_path: str, image_name: str):
    image_path = os.path.join(image_folder_path, image_name)
    if not os.path.exists(image_path) and not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image '{image_name}' not found in '{image_folder_path}'.")
    return cv2.imread(image_path, cv2.IMREAD_UNCHANGED)


class Preparer:

    RED = "red"
    BLUE = "blue"
    image_folder_path = "src\\bot\\states\\in_combat\\sub_state\\preparing\\images"
    fight_lock_off_icon = _load_image(image_folder_path, "fight_lock_off.png")
    fight_lock_off_icon_mask = ImageDetection.create_mask(fight_lock_off_icon)
    fight_lock_on_icon = _load_image(image_folder_path, "fight_lock_on.png")
    fight_lock_on_icon_mask = ImageDetection.create_mask(fight_lock_on_icon)
    tactical_mode_off_icon = _load_image(image_folder_path, "tactical_mode_off.png")
    tactical_mode_off_icon_mask = ImageDetection.create_mask(tactical_mode_off_icon)
    tactical_mode_on_icon = _load_image(image_folder_path, "tactical_mode_on.png")
    tactical_mode_on_icon_mask = ImageDetection.create_mask(tactical_mode_on_icon)
    icon_area = (693, 506, 241, 40)
    ready_button_lit_image = _load_image(image_folder_path, "ready_button_lit.png")
    ready_button_lit_image_mask = ImageDetection.create_mask(ready_button_lit_image)
    ready_button_dim_image = _load_image(image_folder_path, "ready_button_dim.png")
    ready_button_dim_image_mask = ImageDetection.create_mask(ready_button_dim_image)
    ready_button_area = (678, 507, 258, 91)

    def __init__(self, script: str):
        self.__starting_cell_data = MapDataGetter.get_data_object(script).get_starting_cells()
        self.__dummy_cell_data = MapDataGetter.get_data_object(script).get_dummy_cells()

    def prepare(self):
        result = self.handle_fight_lock()
        if (
            result == Status.FAILED_TO_GET_FIGHT_LOCK_ICON_POS
            or result == Status.TIMED_OUT_WHILE_TURNING_ON_FIGHT_LOCK
        ):
            return Status.FAILED_TO_FINISH_PREPARING
        
        result = self.handle_tactical_mode()
        if (
            result == Status.FAILED_TO_GET_TACTICAL_MODE_TOGGLE_ICON_POS
            or result == Status.TIMED_OUT_WHILE_TURNING_ON_TACTICAL_MODE
        ):
            return Status.FAILED_TO_FINISH_PREPARING

        map_coords = MapChanger.get_current_map_coords()
        
        dummy_cell_color = None
        result = self.handle_dummy_cells(map_coords)
        if result == Status.FAILED_TO_MOVE_TO_DUMMY_CELLS:
            return Status.FAILED_TO_FINISH_PREPARING
        else:
            if isinstance(result, str):
                dummy_cell_color = result
        
        result = self.handle_starting_cells(map_coords, dummy_cell_color)
        if result == Status.FAILED_TO_MOVE_TO_STARTING_CELLS:
            return Status.FAILED_TO_FINISH_PREPARING
        
        result = self.handle_clicking_ready()
        if (
            result == Status.FAILED_TO_GET_READY_BUTTON_POS
            or result == Status.TIMED_OUT_WHILE_CLICKING_READY_BUTTON
        ):
            return Status.FAILED_TO_FINISH_PREPARING
        
        return Status.SUCCESSFULLY_FINISHED_PREPARING

    @classmethod
    def handle_fight_lock(cls):
        if cls.is_fight_lock_on():
            log.info("Fight lock is on.")
            return Status.FIGHT_LOCK_IS_ALREADY_ON
        log.info("Fight lock is off.")
        return cls.turn_on_fight_lock()

    @classmethod
    def handle_tactical_mode(cls):
        if cls.is_tactical_mode_on():
            log.info("Tactical mode is on.")
            return Status.TACTICAL_MODE_IS_ALREADY_ON
        log.info("Tactical mode is off.")
        return cls.turn_on_tactical_mode()

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

    @classmethod
    def handle_clicking_ready(cls):
        log.info("Clicking ready ... ")
        ready_button_pos = cls.get_ready_button_pos()
        if ready_button_pos is None:
            log.info("Failed to get ready button position.")
            return Status.FAILED_TO_GET_READY_BUTTON_POS
        
        pyag.moveTo(*ready_button_pos)
        pyag.click()
        move_mouse_off_game_area()

        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if not cls.is_ready_button_visible():
                log.info("Successfully clicked ready button.")
                return Status.SUCCESSFULLY_CLICKED_READY_BUTTON
        log.info("Timed out while clicking ready button.")
        return Status.TIMED_OUT_WHILE_CLICKING_READY_BUTTON

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
        return []

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
        return []

    def get_free_starting_cells(self, map_coords: str, color: str):
        free_cells = []
        for cell_coords in self.get_starting_cells(color, map_coords):
            game_window_screenshot = pyag.screenshot(region=ScreenCapture.game_window_area)
            if self.is_cell_free(*cell_coords, game_window_screenshot):
                free_cells.append(cell_coords)
        return free_cells

    @staticmethod
    def is_cell_free(cell_x, cell_y, game_window_screenshot: Image.Image):
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
        while perf_counter() - start_time <= 0.25:
            if not cls.are_images_same(
                cell_area_before_moving, 
                cls.screenshot_cell_area(cell_x, cell_y)
            ):
                return True
        return False

    @classmethod
    def is_fight_lock_on(cls):
        return not len(
            ImageDetection.find_image(
                haystack=ScreenCapture.custom_area(cls.icon_area),
                needle=cls.fight_lock_off_icon,
                confidence=0.99,
                method=cv2.TM_CCORR_NORMED,
                mask=cls.fight_lock_off_icon_mask
            )
        ) > 0

    @classmethod
    def is_tactical_mode_on(cls):
        return not len(
            ImageDetection.find_image(
                haystack=ScreenCapture.custom_area(cls.icon_area),
                needle=cls.tactical_mode_off_icon,
                confidence=0.98,
                method=cv2.TM_CCORR_NORMED,
                mask=cls.tactical_mode_off_icon_mask
            )
        ) > 0

    @classmethod
    def is_ready_button_visible(cls):
        is_lit_visible = len(
            ImageDetection.find_image(
                haystack=ScreenCapture.custom_area(cls.ready_button_area),
                needle=cls.ready_button_lit_image,
                confidence=0.99,
                method=cv2.TM_CCORR_NORMED,
                mask=cls.ready_button_lit_image_mask
            )
        ) > 0
        is_dim_visible = len(
            ImageDetection.find_image(
                haystack=ScreenCapture.custom_area(cls.ready_button_area),
                needle=cls.ready_button_dim_image,
                confidence=0.99,
                method=cv2.TM_CCORR_NORMED,
                mask=cls.ready_button_dim_image_mask
            )
        ) > 0
        return is_lit_visible or is_dim_visible

    @classmethod
    def get_fight_lock_icon_pos(cls):
        images_to_search = [
            (cls.fight_lock_on_icon, cls.fight_lock_on_icon_mask),
            (cls.fight_lock_off_icon, cls.fight_lock_off_icon_mask)
        ]
        for needle, mask in images_to_search:
            rectangle = ImageDetection.find_image(
                haystack=ScreenCapture.custom_area(cls.icon_area),
                needle=needle,
                confidence=0.99,
                method=cv2.TM_CCORR_NORMED,
                mask=mask
            )
            if len(rectangle) > 0:
                return ImageDetection.get_rectangle_center_point((
                    rectangle[0] + cls.icon_area[0],
                    rectangle[1] + cls.icon_area[1],
                    rectangle[2],
                    rectangle[3]
                ))
        return None

    @classmethod
    def get_tactical_mode_icon_pos(cls):
        images_to_search = [
            (cls.tactical_mode_on_icon, cls.tactical_mode_on_icon_mask),
            (cls.tactical_mode_off_icon, cls.tactical_mode_off_icon_mask)
        ]
        for needle, mask in images_to_search:
            rectangle = ImageDetection.find_image(
                haystack=ScreenCapture.custom_area(cls.icon_area),
                needle=needle,
                confidence=0.98,
                method=cv2.TM_CCORR_NORMED,
                mask=mask
            )
            if len(rectangle) > 0:
                return ImageDetection.get_rectangle_center_point((
                    rectangle[0] + cls.icon_area[0],
                    rectangle[1] + cls.icon_area[1],
                    rectangle[2],
                    rectangle[3]
                ))
        return None

    @classmethod
    def get_ready_button_pos(cls):
        images_to_search = [
            (cls.ready_button_lit_image, cls.ready_button_lit_image_mask),
            (cls.ready_button_dim_image, cls.ready_button_dim_image_mask)
        ]
        for needle, mask in images_to_search:
            rectangle = ImageDetection.find_image(
                haystack=ScreenCapture.custom_area(cls.ready_button_area),
                needle=needle,
                confidence=0.99,
                method=cv2.TM_SQDIFF,
                mask=mask
            )
            if len(rectangle) > 0:
                return ImageDetection.get_rectangle_center_point((
                    rectangle[0] + cls.ready_button_area[0],
                    rectangle[1] + cls.ready_button_area[1],
                    rectangle[2],
                    rectangle[3]
                ))
        return None

    @classmethod
    def turn_on_fight_lock(cls):
        log.info("Turning on fight lock ... ")
        fight_lock_icon_pos = cls.get_fight_lock_icon_pos()
        if fight_lock_icon_pos is None:
            log.info("Failed to get fight lock icon position.")
            return Status.FAILED_TO_GET_FIGHT_LOCK_ICON_POS

        pyag.moveTo(*fight_lock_icon_pos)
        pyag.click()

        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if cls.is_fight_lock_on():
                log.info("Successfully turned on fight lock.")
                return Status.SUCCESSFULLY_TURNED_ON_FIGHT_LOCK
        log.info("Timed out while turning on fight lock.")
        return Status.TIMED_OUT_WHILE_TURNING_ON_FIGHT_LOCK

    @classmethod
    def turn_on_tactical_mode(cls):
        log.info("Turning on tactical mode ... ")
        tactical_mode_icon_pos = cls.get_tactical_mode_icon_pos()
        if tactical_mode_icon_pos is None:
            log.info("Failed to get tactical mode icon position.")
            return Status.FAILED_TO_GET_TACTICAL_MODE_TOGGLE_ICON_POS

        pyag.moveTo(*tactical_mode_icon_pos)
        pyag.click()

        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if cls.is_tactical_mode_on():
                log.info("Successfully turned on tactical mode.")
                return Status.SUCCESSFULLY_TURNED_ON_TACTICAL_MODE
        log.info("Timed out while turning on tactical mode.")
        return Status.TIMED_OUT_WHILE_TURNING_ON_TACTICAL_MODE

from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter

import cv2
import pyautogui as pyag
from PIL import Image

from .map_data.getter import Getter as MapDataGetter
from src.utilities import move_mouse_off_game_area, load_image
from src.bot.states.in_combat.status_enum import Status
from src.bot.map_changer.map_changer import MapChanger
from src.screen_capture import ScreenCapture
from src.image_detection import ImageDetection
from .._combat_options.lock import Lock as FightLock
from .._combat_options.tactical_mode import TacticalMode


class Preparer:

    _IMAGE_FOLDER_PATH = "src\\bot\\states\\in_combat\\sub_state\\preparing\\images"
    _READY_BUTTON_AREA = (678, 507, 258, 91)
    _READY_BUTTON_LIT_IMAGE = load_image(_IMAGE_FOLDER_PATH, "ready_button_lit.png")
    _READY_BUTTON_LIT_IMAGE_MASK = ImageDetection.create_mask(_READY_BUTTON_LIT_IMAGE)
    _READY_BUTTON_DIM_IMAGE = load_image(_IMAGE_FOLDER_PATH, "ready_button_dim.png")
    _READY_BUTTON_DIM_IMAGE_MASK = ImageDetection.create_mask(_READY_BUTTON_DIM_IMAGE)
    _AP_COUNTER_AREA = (452, 598, 41, 48)
    _AP_COUNTER_IMAGE = load_image(_IMAGE_FOLDER_PATH, "ap_counter_image.png")
    _AP_COUNTER_IMAGE_MASK = ImageDetection.create_mask(_AP_COUNTER_IMAGE)
    _RED = "red"
    _BLUE = "blue"

    def __init__(self, script: str):
        self._starting_cell_data = MapDataGetter.get_data_object(script).get_starting_cells()
        self._dummy_cell_data = MapDataGetter.get_data_object(script).get_dummy_cells()

    def prepare(self):
        result = self._handle_fight_lock()
        if (
            result == Status.FAILED_TO_GET_FIGHT_LOCK_ICON_POS
            or result == Status.TIMED_OUT_WHILE_TURNING_ON_FIGHT_LOCK
        ):
            return Status.FAILED_TO_FINISH_PREPARING
        
        result = self._handle_tactical_mode()
        if (
            result == Status.FAILED_TO_GET_TACTICAL_MODE_TOGGLE_ICON_POS
            or result == Status.TIMED_OUT_WHILE_TURNING_ON_TACTICAL_MODE
        ):
            return Status.FAILED_TO_FINISH_PREPARING

        map_coords = MapChanger.get_current_map_coords()
        
        dummy_cell_color = None
        result = self._handle_dummy_cells(map_coords)
        if result == Status.FAILED_TO_MOVE_TO_DUMMY_CELLS:
            return Status.FAILED_TO_FINISH_PREPARING
        else:
            if isinstance(result, str):
                dummy_cell_color = result
                # Prevent character's info tooltip from blocking starting cell locations from view.
                move_mouse_off_game_area() 
        
        result = self._handle_starting_cells(map_coords, dummy_cell_color)
        if result == Status.FAILED_TO_MOVE_TO_STARTING_CELLS:
            return Status.FAILED_TO_FINISH_PREPARING
        
        result = self._handle_clicking_ready()
        if (
            result == Status.FAILED_TO_GET_READY_BUTTON_POS
            or result == Status.TIMED_OUT_WHILE_CLICKING_READY_BUTTON
        ):
            return Status.FAILED_TO_FINISH_PREPARING
        
        result = self._has_combat_started()
        if result == Status.TIMED_OUT_WHILE_DETECTING_START_OF_COMBAT:
            return Status.FAILED_TO_FINISH_PREPARING

        return Status.SUCCESSFULLY_FINISHED_PREPARING

    @staticmethod
    def _handle_fight_lock():
        if FightLock.is_on():
            log.info("Fight lock is on.")
            return Status.FIGHT_LOCK_IS_ALREADY_ON
        log.info("Fight lock is off.")
        return FightLock.turn_on()

    @staticmethod
    def _handle_tactical_mode():
        if TacticalMode.is_on():
            log.info("Tactical mode is on.")
            return Status.TACTICAL_MODE_IS_ALREADY_ON
        log.info("Tactical mode is off.")
        return TacticalMode.turn_on()

    def _handle_dummy_cells(self, map_coords: str):
        log.info(f"Checking for dummy cells on map: {map_coords} ... ")
        red_dummy_cells = self._get_free_dummy_cells(self._RED, map_coords)
        blue_dummy_cells = self._get_free_dummy_cells(self._BLUE, map_coords)
        if len(red_dummy_cells) == 0 and len(blue_dummy_cells) == 0:
            log.info("No dummy cells found on this map.")
            return Status.NO_DUMMY_CELLS_ON_THIS_MAP
        
        log.info("Dummy cells found. Attempting to move ... ")

        for cell_coords in red_dummy_cells:
            status = self._move_char_to_cell(*cell_coords)
            if status == Status.SUCCESSFULLY_MOVED_TO_CELL:
                log.info(f"Successfully moved to red side dummy cell: {cell_coords}.")
                return self._RED
        for cell_coords in blue_dummy_cells:
            status = self._move_char_to_cell(*cell_coords)
            if status == Status.SUCCESSFULLY_MOVED_TO_CELL:
                log.info(f"Successfully moved to blue side dummy cell: {cell_coords}.")
                return self._BLUE
        
        if len(red_dummy_cells) == 0:
            return self._RED
        elif len(blue_dummy_cells) == 0:
            return self._BLUE
        
        log.error("Failed to move to dummy cells.")
        return Status.FAILED_TO_MOVE_TO_DUMMY_CELLS

    def _handle_starting_cells(self, map_coords: str, dummy_cell_color: str = None):
        log.info(f"Attempting to move to a starting cell on map: {map_coords} ... ")
        if dummy_cell_color is not None:
            starting_cells = self._get_free_starting_cells(dummy_cell_color, map_coords)
        else:
            red_starting_cells = self._get_free_starting_cells(self._RED, map_coords)
            blue_starting_cells = self._get_free_starting_cells(self._BLUE, map_coords)
            starting_cells = red_starting_cells + blue_starting_cells

        for cell_coords in starting_cells:
            result = self._move_char_to_cell(*cell_coords)
            if result == Status.SUCCESSFULLY_MOVED_TO_CELL:
                if dummy_cell_color is not None:
                    log.info(f"Successfully moved to {dummy_cell_color} side starting cell: {cell_coords}.")
                else:
                    if cell_coords in red_starting_cells:
                        log.info(f"Successfully moved to red side starting cell: {cell_coords}.")
                    else:
                        log.info(f"Successfully moved to blue side starting cell: {cell_coords}.")
                return Status.SUCCESSFULLY_MOVED_TO_CELL
        
        log.error("Failed to move to a starting cell.")
        return Status.FAILED_TO_MOVE_TO_STARTING_CELLS

    @classmethod
    def _handle_clicking_ready(cls):
        log.info("Clicking ready ... ")
        ready_button_pos = cls._get_ready_button_pos()
        if ready_button_pos is None:
            log.error("Failed to get ready button position.")
            return Status.FAILED_TO_GET_READY_BUTTON_POS
        
        pyag.moveTo(*ready_button_pos)
        pyag.click()
        move_mouse_off_game_area()

        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if not cls._is_ready_button_visible():
                log.info("Successfully clicked ready button.")
                return Status.SUCCESSFULLY_CLICKED_READY_BUTTON
        log.error("Timed out while clicking ready button.")
        return Status.TIMED_OUT_WHILE_CLICKING_READY_BUTTON

    def _move_char_to_cell(self, cell_x, cell_y):
        px_color_before_clicking_cell = pyag.pixel(cell_x, cell_y)
        self._click_cell(cell_x, cell_y)
        if self._did_char_move(cell_x, cell_y, px_color_before_clicking_cell):
            return Status.SUCCESSFULLY_MOVED_TO_CELL
        return Status.FAILED_TO_MOVE_TO_CELL

    def _get_dummy_cells(self, map_coords: str, color: str):
        if color not in [self._RED, self._BLUE]:
            raise ValueError(f"Invalid cell color: '{color}'.")
        for map, cell_data in self._dummy_cell_data.items():
            if map == map_coords:
                return cell_data[color]
        return []

    def _get_free_dummy_cells(self, map_coords: str, color: str):
        free_cells = []
        for cell_coords in self._get_dummy_cells(color, map_coords):
            game_window_screenshot = pyag.screenshot(region=ScreenCapture.GAME_WINDOW_AREA)
            if self._is_cell_free(*cell_coords, game_window_screenshot):
                free_cells.append(cell_coords)
        return free_cells

    def _get_starting_cells(self, map_coords: str, color: str):
        if color not in [self._RED, self._BLUE]:
            raise ValueError(f"Invalid cell color: '{color}'.")
        for map, cell_data in self._starting_cell_data.items():
            if map == map_coords:
                return cell_data[color]
        return []

    def _get_free_starting_cells(self, map_coords: str, color: str):
        free_cells = []
        for cell_coords in self._get_starting_cells(color, map_coords):
            game_window_screenshot = pyag.screenshot(region=ScreenCapture.GAME_WINDOW_AREA)
            if self._is_cell_free(*cell_coords, game_window_screenshot):
                free_cells.append(cell_coords)
        return free_cells

    @staticmethod
    def _is_cell_free(cell_x, cell_y, game_window_screenshot: Image.Image):
        if game_window_screenshot is None:
            game_window_screenshot = pyag.screenshot(region=ScreenCapture.GAME_WINDOW_AREA)
        colors = [
            # There are multiple shades of red and blue because on some maps
            # the "You started a fight!" message makes the cell colors a 
            # bit darker.
            (255, 0, 0), (154, 0, 0), (77, 0, 0), (38, 0, 0), (179, 0, 0)
            (0, 0, 255), (0, 0, 154), (0, 0, 179)
        ]
        for color in colors:
            if game_window_screenshot.getpixel((cell_x, cell_y)) == color:
                return True
        return False

    @staticmethod
    def _are_images_same(before, after):
        return len(
            ImageDetection.find_image(
                haystack=before,
                needle=after,
                method=cv2.TM_CCOEFF_NORMED,
                confidence=0.99
            )
        ) > 0

    @staticmethod
    def _screenshot_cell_area(cell_x, cell_y):
        return ScreenCapture.around_pos((cell_x, cell_y), 30)

    @staticmethod
    def _click_cell(cell_x, cell_y):
        pyag.moveTo(cell_x, cell_y)
        pyag.click()

    @classmethod
    def _did_char_move(cls, cell_x, cell_y, px_color_before_moving: tuple):
        start_time = perf_counter()
        while perf_counter() - start_time <= 0.25:
            if not pyag.pixelMatchesColor(cell_x, cell_y, px_color_before_moving):
                return True
        return False

    @classmethod
    def _is_ready_button_visible(cls):
        is_lit_visible = len(
            ImageDetection.find_image(
                haystack=ScreenCapture.custom_area(cls._READY_BUTTON_AREA),
                needle=cls._READY_BUTTON_LIT_IMAGE,
                confidence=0.99,
                method=cv2.TM_CCORR_NORMED,
                mask=cls._READY_BUTTON_LIT_IMAGE_MASK
            )
        ) > 0
        is_dim_visible = len(
            ImageDetection.find_image(
                haystack=ScreenCapture.custom_area(cls._READY_BUTTON_AREA),
                needle=cls._READY_BUTTON_DIM_IMAGE,
                confidence=0.99,
                method=cv2.TM_CCORR_NORMED,
                mask=cls._READY_BUTTON_DIM_IMAGE_MASK
            )
        ) > 0
        return is_lit_visible or is_dim_visible

    @classmethod
    def _get_ready_button_pos(cls):
        rectangles = ImageDetection.find_images(
            haystack=ScreenCapture.custom_area(cls._READY_BUTTON_AREA),
            needles=[cls._READY_BUTTON_LIT_IMAGE, cls._READY_BUTTON_DIM_IMAGE],
            confidence=0.99,
            method=cv2.TM_SQDIFF,
            masks=[cls._READY_BUTTON_LIT_IMAGE_MASK, cls._READY_BUTTON_DIM_IMAGE_MASK]
        )
        if len(rectangles) > 0:
            return ImageDetection.get_rectangle_center_point((
                rectangles[0][0] + cls._READY_BUTTON_AREA[0],
                rectangles[0][1] + cls._READY_BUTTON_AREA[1],
                rectangles[0][2],
                rectangles[0][3]
            ))
        return None

    @classmethod
    def _is_ap_counter_visible(cls):
        return len(
            ImageDetection.find_image(
                haystack=ScreenCapture.custom_area(cls._AP_COUNTER_AREA),
                needle=cls._AP_COUNTER_IMAGE,
                confidence=0.99,
                mask=cls._AP_COUNTER_IMAGE_MASK
            )
        ) > 0
    
    @classmethod
    def _has_combat_started(cls):
        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if cls._is_ap_counter_visible():
                log.info("Successfully detected the start of combat.")
                return Status.SUCCESSFULLY_DETECTED_START_OF_COMBAT
        log.error("Timed out while detecting the start of combat.")
        return Status.TIMED_OUT_WHILE_DETECTING_START_OF_COMBAT

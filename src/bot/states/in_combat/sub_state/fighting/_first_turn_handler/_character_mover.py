from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter
from math import sqrt

import cv2
import pyautogui as pyag

from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture
from src.bot.map_changer.map_changer import MapChanger
from ..data.getter import Getter as FightingDataGetter
from ._starting_cell_and_side_getter import Getter as StartingCellAndSideGetter
from ..status_enum import Status


class Mover:

    mp_area = (565, 612, 26, 26)

    def __init__(self, script, initial_character_pos):
        self.__initial_character_pos = initial_character_pos
        self.__movement_data = FightingDataGetter.get_data_object(script).get_movement_data()
        self.__starting_side_color = StartingCellAndSideGetter(script).get_starting_side_color(initial_character_pos)

    def move(self):
        coords = self.get_movement_coords()
        
        if self.get_distance_between_cells(coords, self.__initial_character_pos) <= 10:
            log.info(f"Character is already on the correct cell.")
            return Status.CHARACTER_IS_ALREADY_ON_CORRECT_CELL
        
        log.info(f"Attempting to move character to: {coords} ... ")
        pyag.moveTo(coords[0], coords[1])
        if self.is_cell_highlighted(coords):
            mp_area_before_moving = ScreenCapture.custom_area(self.mp_area)
            pyag.click()
            start_time = perf_counter()
            while perf_counter() - start_time <= 5:
                mp_area_after = ScreenCapture.custom_area(self.mp_area)
                rectangle = ImageDetection.find_image(
                    haystack=mp_area_after,
                    needle=mp_area_before_moving,
                    confidence=0.98,
                    method=cv2.TM_CCOEFF_NORMED,
                )
                if len(rectangle) <= 0: # If images are different then moving animation has finished.
                    log.info(f"Successfully moved character to: {coords}.")
                    pyag.moveTo(929, 752) # Move mouse off game area.
                    return Status.SUCCESSFULLY_MOVED_CHARACTER
            log.info(f"Timed out while detecting if character moved to: {coords}.")
            return Status.TIMED_OUT_WHILE_DETECTING_IF_CHARACTER_MOVED
        log.info(f"Failed to detect if destination cell {coords} is highlighted.")
        return Status.FAILED_TO_DETECT_IF_DESTINATION_CELL_IS_HIGHIGHTED
    
    def get_movement_coords(self):
        current_map_coords = MapChanger.get_current_map_coords()
        for map_coords, data in self.__movement_data.items():
            if map_coords == current_map_coords:
                for side_color, click_coords in data.items():
                    if side_color == self.__starting_side_color:
                            if isinstance(click_coords, tuple):
                                return click_coords
                            try:
                                return click_coords[self.__initial_character_pos]
                            except KeyError:
                                raise Exception(
                                    f"No movement data for character position {self.__initial_character_pos} "
                                    f"on starting side color '{self.__starting_side_color}' on map '{map_coords}'."
                                )
        raise Exception(f"No in-combat movement data for map '{current_map_coords}'.")

    def is_cell_highlighted(self, click_coords):
        """
        Checking with a timer to give time for the game to draw orange
        color over the cells after mouse was moved over the destination cell.
        """
        start_time = perf_counter()
        while perf_counter() - start_time <= 3:
            pixel_color_after = pyag.pixel(click_coords[0], click_coords[1])
            if pixel_color_after == (255, 102, 0):
                return True
        return False

    def get_distance_between_cells(self, cell_1, cell_2):
        return sqrt((cell_2[0] - cell_1[0])**2 + (cell_2[1] - cell_1[1])**2)

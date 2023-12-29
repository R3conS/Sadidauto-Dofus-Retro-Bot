from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter
from math import sqrt

import cv2
import pyautogui as pyag

from utilities import move_mouse_off_game_area
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture
from src.bot._map_changer.map_changer import MapChanger
from .._map_data.getter import Getter as FightingDataGetter
from src.bot._states.in_combat._status_enum import Status


class Mover:

    MP_AREA = (565, 612, 26, 26)
    MAX_DISTANCE_BETWEEN_CELLS = 14

    def __init__(self, script: str, character_name: str, current_character_pos: tuple[int, int]):
        self._script = script
        self._character_name = character_name
        self._character_pos = current_character_pos
        self._current_map_coords = MapChanger.get_current_map_coords()
        self._starting_cells_data = FightingDataGetter.get_data_object(script).get_starting_cells()
        self._movement_data = FightingDataGetter.get_data_object(script).get_movement_data()

    def move(self):
        if not self._is_valid_starting_position():
            log.error(f"Character did not start first turn on a valid starting cell.")
            return Status.CHARACTER_DID_NOT_START_FIRST_TURN_ON_VALID_CELL

        if self._is_char_already_on_destination_cell():
            log.info(f"Character is already on the correct cell.")
            move_mouse_off_game_area() # To make sure that info card is not blocking spell bar.
            return Status.CHARACTER_IS_ALREADY_ON_CORRECT_CELL
        
        destination_coords = self._get_destination_cell_coords()
        log.info(f"Attempting to move character to: {destination_coords} ... ")
        pyag.moveTo(destination_coords[0], destination_coords[1])
        if self._is_cell_highlighted(destination_coords):
            mp_area_before_moving = ScreenCapture.custom_area(self.MP_AREA)
            pyag.click()
            start_time = perf_counter()
            while perf_counter() - start_time <= 5:
                mp_area_after = ScreenCapture.custom_area(self.MP_AREA)
                rectangle = ImageDetection.find_image(
                    haystack=mp_area_after,
                    needle=mp_area_before_moving,
                    confidence=0.98,
                    method=cv2.TM_CCOEFF_NORMED,
                )
                if len(rectangle) <= 0: # If images are different then moving animation has finished.
                    log.info(f"Successfully moved character to: {destination_coords}.")
                    move_mouse_off_game_area() # To make sure that character is not hovered over.
                    return Status.SUCCESSFULLY_MOVED_CHARACTER
            log.error(f"Timed out while detecting if character moved to: {destination_coords}.")
            return Status.TIMED_OUT_WHILE_DETECTING_IF_CHARACTER_MOVED
        log.error(f"Failed to detect if destination cell {destination_coords} is highlighted.")
        return Status.FAILED_TO_DETECT_IF_DESTINATION_CELL_IS_HIGHIGHTED
    
    @staticmethod
    def _is_cell_highlighted(click_coords):
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

    def _is_valid_starting_position(self):
        for map_coords, data in self._starting_cells_data.items():
            if map_coords == self._current_map_coords:
                for _, starting_cells_coords in data.items():
                    for coords in starting_cells_coords:
                        if self._get_distance_between_cells(
                            self._character_pos, 
                            coords
                        ) <= self.MAX_DISTANCE_BETWEEN_CELLS:
                            return True
        return False

    def _is_char_already_on_destination_cell(self):
        if self._get_distance_between_cells(
            self._get_destination_cell_coords(), 
            self._character_pos
        ) <= self.MAX_DISTANCE_BETWEEN_CELLS:
            return True
        return False

    def _get_destination_cell_coords(self):
        if not self._are_map_coords_in_data(self._current_map_coords, self._movement_data):
            raise Exception(
                f"Failed to determine destination coords because map '{self._current_map_coords}' "
                "is not in movement data."
            )
        for map_coords, data in self._movement_data.items():
            if map_coords == self._current_map_coords:
                for starting_side_color, starting_cells_coords in data.items():
                    if starting_side_color == self._get_starting_side_color():
                        starting_cell_coords = self._get_starting_cell_coords()
                        try:
                            return starting_cells_coords[starting_cell_coords]
                        except KeyError:
                            raise KeyError(
                                f"Key '{starting_cell_coords}' doesn't exist in movement data for map "
                                f"'{self._current_map_coords}' and starting side color '{starting_side_color}'."
                            )

    def _get_starting_side_color(self):
        if not self._are_map_coords_in_data(self._current_map_coords, self._starting_cells_data):
            raise Exception(
                f"Failed to determine starting side color because map '{self._current_map_coords}' "
                "is not in starting cells data."
            )
        for map_coords, data in self._starting_cells_data.items():
            if map_coords == self._current_map_coords:
                for side_color, starting_cells_coords in data.items():
                    for coords in starting_cells_coords:
                        if self._get_distance_between_cells(
                            self._character_pos, 
                            coords
                        ) <= self.MAX_DISTANCE_BETWEEN_CELLS:
                            return side_color
        raise Exception(
            f"No suitable starting cells were found within {self.MAX_DISTANCE_BETWEEN_CELLS} pixels "
            f"of the given character position '{self._character_pos}' on map "
            f"'{self._current_map_coords}' to determine the starting side color. This most "
            "likely means that the character is not positioned on a valid starting cell."
        )

    def _get_starting_cell_coords(self):
        if not self._are_map_coords_in_data(self._current_map_coords, self._starting_cells_data):
            raise Exception(
                f"Failed to determine starting cell coords because map '{self._current_map_coords}' "
                "is not in starting cells data."
            )
        for map_coords, data in self._starting_cells_data.items():
            if map_coords == self._current_map_coords:
                for starting_side_color, starting_cells_coords in data.items():
                    if starting_side_color == self._get_starting_side_color():
                        for coords in starting_cells_coords:
                            if self._get_distance_between_cells(
                                self._character_pos, 
                                coords
                            ) <= self.MAX_DISTANCE_BETWEEN_CELLS:
                                return coords
        raise Exception(
            f"No suitable starting cells were found within {self.MAX_DISTANCE_BETWEEN_CELLS} pixels "
            f"of the given character position '{self._character_pos}' on map "
            f"'{self._current_map_coords}' to determine the starting cell coords. This most "
            "likely means that the character is not positioned on a valid starting cell."
        )

    @staticmethod
    def _get_distance_between_cells(cell_1: tuple[int, int], cell_2: tuple[int, int]):
        return sqrt((cell_2[0] - cell_1[0])**2 + (cell_2[1] - cell_1[1])**2)

    @staticmethod
    def _are_map_coords_in_data(map_coords: str, data: dict):
        for coords in data.keys():
            if coords == map_coords:
                return True
        return False

from src.logger import Logger
log = Logger.get_logger()

from math import sqrt
from time import perf_counter

import cv2
import pyautogui as pyag

from src.bot._exceptions import ExceptionReason, RecoverableException, UnrecoverableException
from src.bot._map_changer.map_changer import MapChanger
from src.bot._states.in_combat._sub_states.fighting._map_data.getter import Getter as FightingDataGetter
from src.utilities.general import move_mouse_off_game_area
from src.utilities.image_detection import ImageDetection
from src.utilities.screen_capture import ScreenCapture


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
        if self._is_char_already_on_destination_cell():
            log.info("Character is already on the correct cell.")
            return
        
        try:
            if not self._is_valid_starting_position():
                raise _CharacterDidNotStartTurnOnValidCell("Character did not start first turn on a valid starting cell.")

            destination_coords = self._get_destination_cell_coords()
            log.info(f"Attempting to move character to: {destination_coords} ... ")
            pyag.moveTo(destination_coords[0], destination_coords[1])
            self._wait_cell_highlighted(destination_coords)
            mp_area_before_moving = ScreenCapture.custom_area(self.MP_AREA)
            pyag.click()
            self._wait_char_moved(destination_coords, mp_area_before_moving)
        except (
            _CharacterDidNotStartTurnOnValidCell,
            _FailedToDetectIfCellIsHighlighted, 
            _FailedToDetectIfCharacterMoved
        ):
            raise FailedToMoveCharacter("Failed to move character.")
    
    def _wait_char_moved(self, destination_coords, mp_area_before_moving):
        timeout = 5
        start_time = perf_counter()
        while perf_counter() - start_time <= timeout:
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
                return
        raise _FailedToDetectIfCharacterMoved(
            f"Failed to detect if character moved to: {destination_coords}. "
            f"Timed out: {timeout} seconds."
        )

    @staticmethod
    def _wait_cell_highlighted(click_coords):
        """
        Checking with a timer to give time for the game to draw orange
        color over the cells after mouse was moved over the destination cell.
        """
        timeout = 3
        start_time = perf_counter()
        while perf_counter() - start_time <= timeout:
            pixel_color_after = pyag.pixel(click_coords[0], click_coords[1])
            if pixel_color_after == (255, 102, 0):
                return
        raise _FailedToDetectIfCellIsHighlighted(
            f"Failed to detect if cell {click_coords} is highlighted. "
            f"Timed out: {timeout} seconds."
        )

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
            raise UnrecoverableException(
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
            raise UnrecoverableException(
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
        raise RecoverableException(
            message=f"No suitable starting cells were found within {self.MAX_DISTANCE_BETWEEN_CELLS} pixels "
            f"of the given character position '{self._character_pos}' on map "
            f"'{self._current_map_coords}' to determine the starting side color. This most "
            "likely means that the character is not positioned on a valid starting cell.",
            reason=ExceptionReason.FAILED_TO_GET_STARTING_SIDE_COLOR
        )

    def _get_starting_cell_coords(self):
        if not self._are_map_coords_in_data(self._current_map_coords, self._starting_cells_data):
            raise UnrecoverableException(
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
        raise RecoverableException(
            message=f"No suitable starting cells were found within {self.MAX_DISTANCE_BETWEEN_CELLS} pixels "
            f"of the given character position '{self._character_pos}' on map "
            f"'{self._current_map_coords}' to determine the starting cell coords. This most "
            "likely means that the character is not positioned on a valid starting cell.",
            reason=ExceptionReason.FAILED_TO_GET_STARTING_CELL_COORDS
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


class FailedToMoveCharacter(Exception):

    def __init__(self, message):
        self.message = message
        log.error(f"{message}")
        super().__init__(message)


class _CharacterDidNotStartTurnOnValidCell(Exception):
    
    def __init__(self, message):
        self.message = message
        log.error(f"{message}")
        super().__init__(message)


class _FailedToDetectIfCharacterMoved(Exception):

    def __init__(self, message):
        self.message = message
        log.error(f"{message}")
        super().__init__(message)


class _FailedToDetectIfCellIsHighlighted(Exception):

    def __init__(self, message):
        self.message = message
        log.error(f"{message}")
        super().__init__(message)


if __name__ == "__main__":
    mover = Mover("af_anticlock", "Juni", (0, 0))

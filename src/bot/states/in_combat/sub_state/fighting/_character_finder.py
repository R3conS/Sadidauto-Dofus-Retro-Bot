from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter

import cv2
import numpy as np
import pyautogui as pyag

from src.ocr.ocr import OCR
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture
from src.utilities import load_image, move_mouse_off_game_area
from ._fight_preferences.turn_bar import TurnBar
from .status_enum import Status


class Finder:

    _IMAGE_FOLDER_PATH = "src\\bot\\states\\in_combat\\sub_state\\fighting\\images"
    _RED_CIRCLE_IMAGE = load_image(_IMAGE_FOLDER_PATH, "red_circle.png")
    _RED_CIRCLE_IMAGE_MASK = ImageDetection.create_mask(_RED_CIRCLE_IMAGE)
    _BLUE_CIRCLE_IMAGE = load_image(_IMAGE_FOLDER_PATH, "blue_circle.png")
    _BLUE_CIRCLE_IMAGE_MASK = ImageDetection.create_mask(_BLUE_CIRCLE_IMAGE)
    _TURN_INDICATOR_ARROW_IMAGE = load_image(_IMAGE_FOLDER_PATH, "turn_indicator_arrow.png")
    _TURN_INDICATOR_ARROW_IMAGE_MASK = ImageDetection.create_mask(_TURN_INDICATOR_ARROW_IMAGE)
    _INFO_CARD_NAME_AREA = (593, 598, 225, 28)
    _CIRCLE_DETECTION_AREA = (0, 0, 933, 600)
    _TURN_BAR_AREA = (0, 516, 933, 81)

    @classmethod
    def find_by_circles(cls, character_name: str) -> tuple[int, int]:
        """Find character position on the map by red/blue model circles."""
        log.info("Detecting character position by model circles.")

        red_circle_locations = cls.get_red_circle_locations()
        blue_circle_locations = cls.get_blue_circle_locations()
        if len(red_circle_locations) == 0 or len(blue_circle_locations) == 0:
            raise Exception("Failed to detect circles.")
        
        if len(red_circle_locations) <= len(blue_circle_locations):
            first_locations_list = red_circle_locations
            second_locations_list = blue_circle_locations
        else:
            first_locations_list = blue_circle_locations
            second_locations_list = red_circle_locations

        for location in first_locations_list:
            pyag.moveTo(location[0], location[1])
            cls.wait_for_info_card_to_appear()
            if not cls.is_info_card_visible():
                log.error("Timed out while waiting for info card to appear during detection by circles.")
                return Status.TIMED_OUT_WHILE_WAITING_FOR_INFO_CARD_TO_APPEAR
            name_area = cls.screenshot_name_area_on_info_card()
            if cls.read_name_area_screenshot(name_area) == character_name:
                log.info(f"Found character at: {location}")
                return location
            
        for location in second_locations_list:
            pyag.moveTo(location[0], location[1])
            cls.wait_for_info_card_to_appear()
            if not cls.is_info_card_visible():
                log.error("Timed out while waiting for info card to appear during detection by circles.")
                return Status.TIMED_OUT_WHILE_WAITING_FOR_INFO_CARD_TO_APPEAR
            name_area = cls.screenshot_name_area_on_info_card()
            if cls.read_name_area_screenshot(name_area) == character_name:
                log.info(f"Found character at: {location}")
                return location
            
        raise Exception("Failed to find character by circles.")

    @classmethod
    def find_by_turn_bar(cls, character_name: str) -> tuple[int, int]:
        """Find the character's card on the turn bar."""
        log.info("Detecting character position by turn bar.")

        if TurnBar.is_shrunk():
            if TurnBar.unshrink() == Status.TIMED_OUT_WHILE_UNSHRINKING_TURN_BAR:
                return Status.TIMED_OUT_WHILE_UNSHRINKING_TURN_BAR

        turn_arrow = cls._get_turn_indicator_arrow_location()
        if turn_arrow is None:
            log.error("Failed to get turn indicator arrow location.")
            return Status.FAILED_TO_GET_TURN_INDICATOR_ARROW_LOCATION
        
        pyag.moveTo(turn_arrow[0], turn_arrow[1])
        pyag.moveRel(-10, 30) # Moving mouse onto the turn card.
        cls.wait_for_info_card_to_appear()
        if not cls.is_info_card_visible():
            log.error("Timed out while waiting for info card to appear during detection by turn bar.")
            move_mouse_off_game_area() # To stop info card from staying on screen.
            return Status.TIMED_OUT_WHILE_WAITING_FOR_INFO_CARD_TO_APPEAR

        name_area = cls.screenshot_name_area_on_info_card()
        name = cls.read_name_area_screenshot(name_area)
        if name == character_name:
            turn_card_pos = pyag.position()
            log.info(f"Found character at: {turn_card_pos[0], turn_card_pos[1]}")
            move_mouse_off_game_area() # To stop info card from staying on screen.
            return turn_card_pos
        
        raise Exception(f"Failed to read correct name. Expected: '{character_name}', got: '{name}'.")

    @classmethod
    def get_red_circle_locations(cls) -> list[tuple[int, int]]:
        """Get red model circle locations."""
        rectangles = ImageDetection.find_image(
            haystack=cls._screenshot_circle_detection_area(),
            needle=cls._RED_CIRCLE_IMAGE,
            method=cv2.TM_CCORR_NORMED,
            confidence=0.85,
            mask=cls._RED_CIRCLE_IMAGE_MASK,
            get_best_match_only=False
        )
        rectangles = cv2.groupRectangles(rectangles, 1, 0.5)[0]
        center_points = []
        if len(rectangles) > 0:
            for rectangle in rectangles:
                center_points.append(ImageDetection.get_rectangle_center_point(rectangle))
        return center_points

    @classmethod
    def get_blue_circle_locations(cls) -> list[tuple[int, int]]:
        """Get blue model circle locations."""
        rectangles = ImageDetection.find_image(
            haystack=cls._screenshot_circle_detection_area(),
            needle=cls._BLUE_CIRCLE_IMAGE,
            method=cv2.TM_CCORR_NORMED,
            confidence=0.85,
            mask=cls._BLUE_CIRCLE_IMAGE_MASK,
            get_best_match_only=False
        )
        rectangles = cv2.groupRectangles(rectangles, 1, 0.5)[0]
        center_points = []
        if len(rectangles) > 0:
            for rectangle in rectangles:
                center_points.append(ImageDetection.get_rectangle_center_point(rectangle))
        return center_points

    @classmethod
    def _get_turn_indicator_arrow_location(cls):
        """Make sure the turn bar is not shrunk for accurate results."""
        rectangle = ImageDetection.find_image(
            haystack=cls._screenshot_turn_bar_area(),
            needle=cls._TURN_INDICATOR_ARROW_IMAGE,
            method=cv2.TM_SQDIFF,
            confidence=0.99,
            mask=cls._TURN_INDICATOR_ARROW_IMAGE_MASK,
        )
        if len(rectangle) > 0:
            return ImageDetection.get_rectangle_center_point((
                rectangle[0] + cls._TURN_BAR_AREA[0],
                rectangle[1] + cls._TURN_BAR_AREA[1],
                rectangle[2],
                rectangle[3]
            ))
        
        return None
        
    @classmethod
    def screenshot_name_area_on_info_card(cls):
        return ScreenCapture.custom_area(cls._INFO_CARD_NAME_AREA)    

    @classmethod
    def _screenshot_circle_detection_area(cls):
        """No chat, no minimap, no spell & item bars."""
        return ScreenCapture.custom_area(cls._CIRCLE_DETECTION_AREA)

    @classmethod
    def _screenshot_turn_bar_area(cls):
        return ScreenCapture.custom_area(cls._TURN_BAR_AREA)

    @staticmethod
    def read_name_area_screenshot(screenshot: np.ndarray):
        return OCR.get_text_from_image(OCR.convert_to_grayscale(screenshot))

    @staticmethod
    def is_info_card_visible():
        pixels = {
            (612, 635): (255, 255, 255),
            (576, 749): (184, 177, 143),
            (926, 748): (184, 177, 143)
        }
        match_results = []
        for pixel, color in pixels.items():
            match_results.append(pyag.pixelMatchesColor(pixel[0], pixel[1], color))
        return all(match_results)

    @classmethod
    def wait_for_info_card_to_appear(cls):
        start_time = perf_counter()
        while perf_counter() - start_time <= 1.5:
            if cls.is_info_card_visible():
                return True
        return False

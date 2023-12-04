from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import os
from time import perf_counter

import cv2
import numpy as np
import pyautogui as pyag

from src.ocr.ocr import OCR
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture
from src.utilities import load_image
from .._fight_preferences.turn_bar import TurnBar
from ..status_enum import Status


class Finder:

    # ToDo: return Status values instead of raising exceptions in some methods.

    image_folder_path = "src\\bot\\states\\in_combat\\sub_state\\fighting\\images"
    red_circle_image = load_image(image_folder_path, "red_circle.png")
    red_circle_image_mask = ImageDetection.create_mask(red_circle_image)
    blue_circle_image = load_image(image_folder_path, "blue_circle.png")
    blue_circle_image_mask = ImageDetection.create_mask(blue_circle_image)
    turn_indicator_arrow_image = load_image(image_folder_path, "turn_indicator_arrow.png")
    turn_indicator_arrow_image_mask = ImageDetection.create_mask(turn_indicator_arrow_image)
    info_card_name_area = (593, 598, 225, 28)
    circle_detection_area = (0, 0, 933, 600)
    turn_bar_area = (0, 516, 933, 81)

    def __init__(self, character_name: str):
        self.character_name = character_name

    def find_by_circles(self) -> tuple[int, int]:
        """Find character position on the map by red/blue model circles."""
        red_circle_locations = self.get_red_circle_locations()
        blue_circle_locations = self.get_blue_circle_locations()
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
            self.wait_for_info_card_to_appear()
            if not self.is_info_card_visible():
                raise Exception("Timed out while waiting for info card to appear.")
            name_area = self.screenshot_name_area_on_info_card()
            if self.read_name_area_screenshot(name_area) == self.character_name:
                return location
            
        for location in second_locations_list:
            pyag.moveTo(location[0], location[1])
            self.wait_for_info_card_to_appear()
            if not self.is_info_card_visible():
                raise Exception("Timed out while waiting for info card to appear.")
            name_area = self.screenshot_name_area_on_info_card()
            if self.read_name_area_screenshot(name_area) == self.character_name:
                return location
            
        raise Exception("Failed to find character by circles.")

    def find_by_turn_bar(self) -> tuple[int, int]:
        """Find the character's card on the turn bar."""
        turn_arrow = self.get_turn_indicator_arrow_location()
        if turn_arrow is None:
            raise Exception("Failed to detect turn indicator arrow.")
        
        pyag.moveTo(turn_arrow[0], turn_arrow[1])
        pyag.moveRel(-10, 30) # Moving mouse onto the turn card.
        self.wait_for_info_card_to_appear()
        if not self.is_info_card_visible():
            raise Exception("Timed out while waiting for info card to appear.")

        name_area = self.screenshot_name_area_on_info_card()
        name = self.read_name_area_screenshot(name_area)
        if name == self.character_name:
            return pyag.position()
        
        raise Exception(f"Failed to read correct name. Expected: '{self.character_name}', got: '{name}'.")

    @classmethod
    def get_red_circle_locations(cls):
        rectangles = ImageDetection.find_image(
            haystack=cls.screenshot_circle_detection_area(),
            needle=cls.red_circle_image,
            method=cv2.TM_SQDIFF,
            confidence=0.9,
            mask=cls.red_circle_image_mask,
            get_best_match_only=False
        )
        rectangles = cv2.groupRectangles(rectangles, 1, 0.5)[0]
        center_points = []
        if len(rectangles) > 0:
            for rectangle in rectangles:
                center_points.append(ImageDetection.get_rectangle_center_point(rectangle))
        return center_points

    @classmethod
    def get_blue_circle_locations(cls):
        rectangles = ImageDetection.find_image(
            haystack=cls.screenshot_circle_detection_area(),
            needle=cls.blue_circle_image,
            method=cv2.TM_SQDIFF,
            confidence=0.9,
            mask=cls.blue_circle_image_mask,
            get_best_match_only=False
        )
        rectangles = cv2.groupRectangles(rectangles, 1, 0.5)[0]
        center_points = []
        if len(rectangles) > 0:
            for rectangle in rectangles:
                center_points.append(ImageDetection.get_rectangle_center_point(rectangle))
        return center_points

    @classmethod
    def get_turn_indicator_arrow_location(cls):
        if TurnBar.is_shrunk():
            if TurnBar.unshrink() == Status.TIMED_OUT_WHILE_UNSHRINKING_TURN_BAR:
                return None
            
        rectangle = ImageDetection.find_image(
            haystack=cls.screenshot_turn_bar_area(),
            needle=cls.turn_indicator_arrow_image,
            method=cv2.TM_CCORR_NORMED,
            confidence=0.9,
            mask=cls.turn_indicator_arrow_image_mask,
        )
        if len(rectangle) > 0:
            return ImageDetection.get_rectangle_center_point((
                rectangle[0] + cls.turn_bar_area[0],
                rectangle[1] + cls.turn_bar_area[1],
                rectangle[2],
                rectangle[3]
            ))
        
        return None
        
    @classmethod
    def screenshot_name_area_on_info_card(cls):
        return ScreenCapture.custom_area(cls.info_card_name_area)    

    @classmethod
    def screenshot_circle_detection_area(cls):
        """No chat, no minimap, no spell & item bars."""
        return ScreenCapture.custom_area(cls.circle_detection_area)

    @classmethod
    def screenshot_turn_bar_area(cls):
        return ScreenCapture.custom_area(cls.turn_bar_area)

    @staticmethod
    def read_name_area_screenshot(screenshot: np.ndarray):
        return OCR.get_text_from_image(
            OCR.convert_to_grayscale(screenshot), 
            ocr_engine="tesserocr"
        )

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
        while perf_counter() - start_time <= 3:
            if cls.is_info_card_visible():
                return True
        return False

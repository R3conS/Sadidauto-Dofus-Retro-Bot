from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import os

import cv2
import numpy as np
import pyautogui as pyag

from src.ocr.ocr import OCR
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture


def _load_image(image_folder_path: str, image_name: str):
    image_path = os.path.join(image_folder_path, image_name)
    if not os.path.exists(image_path) and not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image '{image_name}' not found in '{image_folder_path}'.")
    return cv2.imread(image_path, cv2.IMREAD_UNCHANGED)


class Finder:

    image_folder_path = "src\\bot\\states\\in_combat\\sub_state\\fighting\\images"
    red_circle_image = _load_image(image_folder_path, "red_circle.png")
    red_circle_image_mask = ImageDetection.create_mask(red_circle_image)
    blue_circle_image = _load_image(image_folder_path, "blue_circle.png")
    blue_circle_image_mask = ImageDetection.create_mask(blue_circle_image)

    def __init__(self, character_name: str):
        self.character_name = character_name

    def find(self):
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
            name_area = self.screenshot_name_area_on_info_card()
            if self.read_name_area_screenshot(name_area) == self.character_name:
                return location
            
        for location in second_locations_list:
            pyag.moveTo(location[0], location[1])
            name_area = self.screenshot_name_area_on_info_card()
            if self.read_name_area_screenshot(name_area) == self.character_name:
                return location
            
        raise Exception("Failed to find character.")

    @classmethod
    def get_red_circle_locations(cls):
        rectangles = ImageDetection.find_image(
            haystack=cls.screenshot_detection_area(),
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
            haystack=cls.screenshot_detection_area(),
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

    @staticmethod
    def screenshot_name_area_on_info_card():
        return ScreenCapture.custom_area((593, 598, 225, 28))    

    @staticmethod
    def screenshot_detection_area():
        """No chat, no minimap, no spell & item bars."""
        return ScreenCapture.custom_area((0, 0, 933, 600))

    @staticmethod
    def read_name_area_screenshot(screenshot: np.ndarray):
        return OCR.get_text_from_image(
            OCR.convert_to_grayscale(screenshot), 
            ocr_engine="tesserocr"
        )

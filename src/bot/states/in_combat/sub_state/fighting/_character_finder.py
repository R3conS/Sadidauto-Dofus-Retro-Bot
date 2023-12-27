from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter

import cv2
import numpy as np
import pyautogui as pyag
from sklearn.cluster import DBSCAN
from PIL import Image

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
    _INFO_CARD_NAME_AREA = (593, 598, 225, 28)
    _CIRCLE_DETECTION_AREA = (0, 0, 933, 600)
    _TURN_BAR_AREA = (0, 516, 933, 77)

    @classmethod
    def find_by_circles(cls, character_name: str) -> tuple[int, int]:
        """Find character position on the map by red model circles."""
        log.info("Detecting character position by model circles.")

        red_circle_locations = cls.get_red_circle_locations()
        if len(red_circle_locations) == 0:
            raise Exception("Failed to detect circles.")
        
        for location in red_circle_locations:
            pyag.moveTo(location[0], location[1])
            cls.wait_for_info_card_to_appear()
            if not cls.is_info_card_visible():
                log.error("Timed out while waiting for info card to appear during detection by circles.")
                continue
            name_area = cls.screenshot_name_area_on_info_card()
            if cls.read_name_area_screenshot(name_area) == character_name:
                log.info(f"Found character at: {location}")
                move_mouse_off_game_area()
                return location
            
        raise Exception("Failed to find character by circles.")

    @classmethod
    def find_by_turn_bar(cls, character_name: str) -> tuple[int, int]:
        """Find the character's card on the turn bar."""
        log.info("Detecting character position by turn bar.")

        if TurnBar.is_shrunk():
            if TurnBar.unshrink() == Status.TIMED_OUT_WHILE_UNSHRINKING_TURN_BAR:
                return Status.TIMED_OUT_WHILE_UNSHRINKING_TURN_BAR

        red_health_pixels = cls._find_pixels(cls._screenshot_turn_bar_area(), (255, 0, 0))
        clustered_pixels = cls._cluster_pixels(red_health_pixels)
        middle_pixels = [cls._find_most_middle_pixel(cluster) for cluster in clustered_pixels.values()]
        for pixel_loc in middle_pixels:
            if pixel_loc is not None:
                pyag.moveTo(*pixel_loc)
                cls.wait_for_info_card_to_appear()
                if not cls.is_info_card_visible():
                    log.error("Timed out while waiting for info card to appear during detection by turn bar.")
                    move_mouse_off_game_area()
                    return Status.TIMED_OUT_WHILE_WAITING_FOR_INFO_CARD_TO_APPEAR

                name_area = cls.screenshot_name_area_on_info_card()
                name = cls.read_name_area_screenshot(name_area)
                if name == character_name:
                    log.info(f"Found character at: {pixel_loc[0], pixel_loc[1]}")
                    move_mouse_off_game_area()
                    return pixel_loc
        
        return Status.FAILED_TO_GET_CHARACTER_POS_BY_TURN_BAR

    @classmethod
    def get_red_circle_locations(cls) -> list[tuple[int, int]]:
        """Get red model circle locations."""
        rectangles = ImageDetection.find_image(
            haystack=cls._screenshot_circle_detection_area(),
            needle=cls._RED_CIRCLE_IMAGE,
            method=cv2.TM_CCORR_NORMED,
            confidence=0.86,
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
            confidence=0.86,
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

    @classmethod
    def _find_pixels(cls, image: np.ndarray | Image.Image, rgb_color):
        if isinstance(image, np.ndarray):
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
        elif isinstance(image, Image.Image):
            if image.mode == "BGR":
                image = image.convert("RGB")

        pixels = []
        for y in range(image.height):
            for x in range(image.width):
                r, g, b = image.getpixel((x, y)) # ScreenCapture.custom_area() returns in BGR.
                if (r, g, b) == rgb_color: 
                    pixels.append((x + cls._TURN_BAR_AREA[0], y + cls._TURN_BAR_AREA[1]))
        return pixels

    @staticmethod
    def _cluster_pixels(
            pixels: list[tuple[int, int]],
            eps: int = 15,
            min_samples: int = 2,
        ) -> dict[int, list[tuple[int, int]]]:
        if len(pixels) == 0:
            return {}
        db = DBSCAN(eps=eps, min_samples=min_samples)
        labels = db.fit_predict(pixels)
        clusters_dict = {}
        for i, label in enumerate(labels):
            if label != -1:
                if label not in clusters_dict:
                    clusters_dict[label] = []
                clusters_dict[label].append(tuple(pixels[i]))
        return clusters_dict

    @staticmethod
    def _find_most_middle_pixel(pixel_cluster: list[tuple[int, int]]):
        if len(pixel_cluster) == 0:
            return None
        pixel_cluster = np.array(pixel_cluster)
        center = pixel_cluster.mean(axis=0)
        distances = np.sqrt(np.sum((pixel_cluster - center)**2, axis=1))
        closest_index = np.argmin(distances)
        return pixel_cluster[closest_index]

import cv2
import numpy as np
import pyautogui as pyag

from src.utilities.general import load_image_full_path
from src.utilities.image_detection import ImageDetection
from src.utilities.screen_capture import ScreenCapture


class RoughTooltipGetter:

    LEVEL_IMAGE = load_image_full_path("src\\bot\\_states\\out_of_combat\\_sub_states\\hunting\\_monster_finder\\_images\\level_text_on_monster_tooltip.png")

    @classmethod
    def get_rough_tooltip_images(cls) -> tuple[list[np.ndarray], list[tuple[int, int, int, int]], np.ndarray]:
        """
        Returns a list of tooltip images, a list of areas that were 
        used to crop them and the image where they were cropped from.
        """
        haystack = cls._get_image_to_search_on()
        text_locations = cls._get_level_text_locations(haystack)
        crop_areas = cls._calculate_tooltip_crop_areas(text_locations)
        crop_outs = cls._crop_out_rough_tooltip_areas(haystack, crop_areas)
        return crop_outs, crop_areas, haystack

    @staticmethod
    def _get_image_to_search_on():
        pyag.keyDown("z")
        screenshot = ScreenCapture.game_window()
        pyag.keyUp("z")
        return screenshot

    @classmethod
    def _get_level_text_locations(cls, image_to_search_on) -> list[tuple[int, int]]:
        """Returns a list of center points of the 'Level' text on the monster tooltips."""
        rectangles = ImageDetection.find_image(
            haystack=image_to_search_on,
            needle=cls.LEVEL_IMAGE,
            confidence=0.75,
            method=cv2.TM_CCOEFF_NORMED,
            get_best_match_only=False
        )
        # Duplicating so that close rectangles can be grouped properly.
        rectangles = [rect for rect in rectangles for _ in range(2)]
        rectangles = cv2.groupRectangles(rectangles, 1, 0.5)[0]
        return [ImageDetection.get_rectangle_center_point(rect) for rect in rectangles]

    @staticmethod
    def _calculate_tooltip_crop_area(level_text_center_point: tuple[int, int]) -> tuple[int, int, int, int]:
        """Calculate the rough area (x, y, w, h) of the tooltip based on the location of the 'Level' text."""
        top_left_x = level_text_center_point[0] - 35
        if top_left_x < 0:
            top_left_x = 0
        top_left_y = level_text_center_point[1] - 15
        if top_left_y < 0:
            top_left_y = 0
        bottom_right_x = level_text_center_point[0] + 56
        bottom_right_y = level_text_center_point[1] + 182
        return (
            int(top_left_x),
            int(top_left_y),
            int(bottom_right_x - top_left_x),
            int(bottom_right_y - top_left_y)
        )

    @classmethod
    def _calculate_tooltip_crop_areas(cls, level_text_center_points: list[tuple[int, int]]):
        """Calculate the rough areas (x, y, w, h) of the tooltips based on the locations of the 'Level' text."""
        return [cls._calculate_tooltip_crop_area(center_point) for center_point in level_text_center_points]

    @staticmethod
    def _crop_out_rough_tooltip_area(haystack: np.ndarray, crop_area: tuple[int, int, int, int]):
        """Crops out the tooltip area based on the location of the 'Level' text."""
        return haystack[crop_area[1]:crop_area[1]+crop_area[3], crop_area[0]:crop_area[0]+crop_area[2]]

    @classmethod
    def _crop_out_rough_tooltip_areas(cls, haystack: np.ndarray, crop_areas) -> list[np.ndarray]:
        """Crops out the tooltip areas based on locations of the 'Level' text."""
        return [cls._crop_out_rough_tooltip_area(haystack, crop_area) for crop_area in crop_areas]
    

if __name__ == "__main__":
    from time import sleep
    sleep(0.5)
    crop_outs, crop_areas, haystack = RoughTooltipGetter.get_rough_tooltip_images()
    for i, crop_out in enumerate(crop_outs):
        cv2.imshow("cropped", crop_out)
        cv2.waitKey(0)

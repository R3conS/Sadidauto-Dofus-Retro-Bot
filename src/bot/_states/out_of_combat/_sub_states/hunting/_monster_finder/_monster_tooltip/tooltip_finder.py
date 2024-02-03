import cv2
import numpy as np
import pyautogui as pyag

from src.bot._states.out_of_combat._sub_states.hunting._monster_finder._monster_tooltip._sorter import Sorter
from src.bot._states.out_of_combat._sub_states.hunting._monster_finder._monster_tooltip._tooltip import Tooltip
from src.utilities.general import load_image_full_path
from src.utilities.image_detection import ImageDetection
from src.utilities.screen_capture import ScreenCapture


class TooltipFinder:

    LEVEL_IMAGE = load_image_full_path("src\\bot\\_states\\out_of_combat\\_sub_states\\hunting\\_monster_finder\\_monster_tooltip\\_images\\level.png")

    @classmethod
    def get_tooltips(cls) -> list[Tooltip]:
        haystack = cls._get_image_to_search_on()
        text_locations = cls._get_level_text_center_points(haystack)
        tooltips = [Tooltip(haystack, location) for location in text_locations]
        sorted_tooltips = Sorter.sort(tooltips, Sorter.SORT_BY_TOOLTIP_RECTANGLE_AREA)
        return sorted_tooltips

    @staticmethod
    def _get_image_to_search_on():
        pyag.keyDown("z")
        screenshot = ScreenCapture.game_window()
        pyag.keyUp("z")
        return screenshot

    @classmethod
    def _get_level_text_center_points(cls, image_to_search_on) -> list[tuple[int, int]]:
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

    @classmethod
    def __get_and_display_all_tooltips(cls):
        """Used for debugging purposes."""
        from time import sleep

        # Give some time to activate game window, otherwise '_get_image_to_search_on()' 
        # won't trigger tooltips in the game.
        sleep(1)
        haystack = cls._get_image_to_search_on()
        text_locations = cls._get_level_text_center_points(haystack)
        for location in text_locations:
            tooltip = Tooltip(haystack, location)
            print(f"\nMoster counts: {tooltip.monster_counts}")
            print(f"Rectangle: {tooltip.rectangle}")
            print(f"Rectangle area: {tooltip.rectangle_area}")
            print(f"Top middle point: {tooltip.top_middle_point}")
            print(f"Bottom middle point: {tooltip.bottom_middle_point}")
            haystack = ImageDetection.draw_rectangle(haystack, tooltip.rectangle)
            haystack = ImageDetection.draw_marker(haystack, tooltip.top_middle_point, color=(0, 0, 255))
            haystack = ImageDetection.draw_marker(haystack, tooltip.bottom_middle_point, color=(0, 0, 255))
        cv2.imshow("haystack", haystack)
        cv2.waitKey(0)


if __name__ == "__main__":
    from time import sleep

    # TooltipFinder._TooltipFinder__get_and_display_all_tooltips()
    sleep(0.5)
    tooltips = TooltipFinder.get_tooltips()
    sorted_tooltips = Sorter.sort(tooltips, Sorter.SORT_BY_MONSTER_PRIORITY)
    for tooltip in sorted_tooltips:
        print(tooltip.monster_counts)

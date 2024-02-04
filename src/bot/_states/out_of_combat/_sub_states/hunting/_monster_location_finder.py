import cv2
import pyautogui as pyag

from src.bot._states.out_of_combat._sub_states.hunting._monster_tooltip_finder.tooltip import Tooltip
from src.utilities.general import load_image_full_path
from src.utilities.image_detection import ImageDetection
from src.utilities.screen_capture import ScreenCapture


class MonsterLocationFinder:

    LEVEL_IMAGE = load_image_full_path("src\\bot\\_states\\out_of_combat\\_sub_states\\hunting\\_images\\level.png")

    @classmethod
    def get_monster_location(cls, monster_tooltip: Tooltip):
        monster_locations = cls._get_possible_monster_locations(monster_tooltip.rectangle)
        for location in monster_locations.values():
            if cls._is_monster_at_location(location):
                return location
        return None

    @staticmethod
    def _get_possible_monster_locations(tooltip_rectangle):
        """
        Monsters always stand at a fixed pixel distance from the tooltip.
        Usually at the bottom or at the top. If the monster is near the 
        left or right edge of the game window, then it may stand slightly 
        to the left or right of the middle points.
        """
        bottom_middle = (
            int(tooltip_rectangle[0] + tooltip_rectangle[2] // 2), 
            tooltip_rectangle[1] + tooltip_rectangle[3] + 35
        )
        top_middle = (
            int(tooltip_rectangle[0] + tooltip_rectangle[2] // 2), 
            tooltip_rectangle[1] - 20
        )
        return {
            "bottom_middle": bottom_middle,
            "top_middle": top_middle,
            "bottom_left": (bottom_middle[0] - 22, bottom_middle[1]),
            "bottom_right": (bottom_middle[0] + 22, bottom_middle[1]),
            "top_left": (top_middle[0] - 22, top_middle[1]),
            "top_right": (top_middle[0] + 22, top_middle[1])
        }

    @classmethod
    def _is_level_text_visible_around_point(cls, point):
        top_left_x = point[0] - 60 if point[0] - 60 > 0 else 0
        width = 140
        if top_left_x + width > ScreenCapture.GAME_WINDOW_AREA[2]:
            width = ScreenCapture.GAME_WINDOW_AREA[2] - top_left_x
        return len(
            ImageDetection.find_image(
                haystack=ScreenCapture.custom_area((top_left_x, 0, 140, ScreenCapture.GAME_WINDOW_AREA[3])),
                needle=cls.LEVEL_IMAGE,
                confidence=0.7,
                method=cv2.TM_CCOEFF_NORMED,
                get_best_match_only=False
            )
        ) > 0

    @classmethod
    def _is_monster_at_location(cls, location):
        pyag.moveTo(*location)   
        return cls._is_level_text_visible_around_point(location)


if __name__ == "__main__":
    print(MonsterLocationFinder._is_level_text_visible_around_point((871, 366)))

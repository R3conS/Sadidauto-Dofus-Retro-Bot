import numpy as np

from src.utilities.general import load_image_full_path
from src.utilities.screen_capture import ScreenCapture


class RoughCropper:

    def __init__(self, image_to_crop_from: np.ndarray | str, level_text_center_point: tuple[int, int]):
        if isinstance(image_to_crop_from, str):
            image_to_crop_from = load_image_full_path(image_to_crop_from)
        self._image_to_crop_from = image_to_crop_from
        self._level_text_center_point = level_text_center_point
        self.crop_area = self._calculate_crop_area(level_text_center_point)
        self.tooltip = self._crop(image_to_crop_from, self.crop_area)

    @staticmethod
    def _calculate_crop_area(level_text_center_point: tuple[int, int]) -> tuple[int, int, int, int]:
        """Calculate the rough area (x, y, w, h) of the tooltip based on the location of the 'Level' text."""
        top_left_x = level_text_center_point[0] - 35
        if top_left_x < 0:
            top_left_x = 0
        top_left_y = level_text_center_point[1] - 15
        if top_left_y < 0:
            top_left_y = 0
        bottom_right_x = level_text_center_point[0] + 56
        if bottom_right_x > ScreenCapture.GAME_WINDOW_AREA[2]:
            bottom_right_x = ScreenCapture.GAME_WINDOW_AREA[2]
        bottom_right_y = level_text_center_point[1] + 182
        if bottom_right_y > ScreenCapture.GAME_WINDOW_AREA[3]:
            bottom_right_y = ScreenCapture.GAME_WINDOW_AREA[3]
        return (
            int(top_left_x),
            int(top_left_y),
            int(bottom_right_x - top_left_x),
            int(bottom_right_y - top_left_y)
        )

    @staticmethod
    def _crop(haystack: np.ndarray, crop_area: tuple[int, int, int, int]) -> np.ndarray:
        """Crops out the tooltip area based on the location of the 'Level' text."""
        return haystack[crop_area[1]: crop_area[1] + crop_area[3], crop_area[0]: crop_area[0] + crop_area[2]]

if __name__ == "__main__":
    # cropper = RoughCropper("haystack.png", (100, 100))
    pass
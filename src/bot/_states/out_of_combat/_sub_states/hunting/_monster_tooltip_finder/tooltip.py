import numpy as np

from src.bot._states.out_of_combat._sub_states.hunting._monster_tooltip_finder._precise_cropper import PreciseCropper
from src.bot._states.out_of_combat._sub_states.hunting._monster_tooltip_finder._reader import Reader
from src.bot._states.out_of_combat._sub_states.hunting._monster_tooltip_finder._rough_cropper import RoughCropper


class Tooltip:

    def __init__(
        self, 
        image_to_crop_from: np.ndarray,
        level_text_center_point: tuple[int, int],
    ):
        self._level_text_center_point = level_text_center_point
        self._image_to_crop_from = image_to_crop_from
        rough_cropper = RoughCropper(self._image_to_crop_from, self._level_text_center_point)
        self._rough_tooltip = rough_cropper.tooltip
        self._rough_tooltip_crop_area = rough_cropper.crop_area
        precise_cropper = PreciseCropper(rough_cropper.tooltip)
        self._precise_tooltip = precise_cropper.tooltip
        self._precise_tooltip_crop_area = precise_cropper.crop_area
        reader = Reader(precise_cropper.tooltip)
        self.monster_counts = reader.monster_counts
        self.rectangle = self._calculate_rectangle()
        self.rectangle_area = self._calculate_rectangle_area()
        self.top_middle_point = self._calculate_top_middle_point()
        self.bottom_middle_point = self._calculate_bottom_middle_point()

    def _calculate_rectangle(self):
        return (
            self._rough_tooltip_crop_area[0] + self._precise_tooltip_crop_area[0],
            self._rough_tooltip_crop_area[1] + self._precise_tooltip_crop_area[1],
            self._precise_tooltip.shape[1],
            self._precise_tooltip.shape[0]
        )

    def _calculate_rectangle_area(self):
        return self._precise_tooltip.shape[0] * self._precise_tooltip.shape[1]

    def _calculate_bottom_middle_point(self):
        return (int(self.rectangle[0] + self.rectangle[2] // 2), self.rectangle[1] + self.rectangle[3])
    
    def _calculate_top_middle_point(self):
        return (int(self.rectangle[0] + self.rectangle[2] // 2), self.rectangle[1])

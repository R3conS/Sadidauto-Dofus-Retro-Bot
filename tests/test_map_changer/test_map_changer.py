import os
import unittest

from src.bot._map_changer._map_data import DATA as MAP_DATA


class TestMapChanger(unittest.TestCase):

    _IMAGE_FOLDER_FOLDER_PATH = "src\\bot\\_map_changer\\_images"

    def test_map_data(self):
        """Make sure that all map coords in map data have a corresponding image file."""
        image_names = []
        for file_name in [name for name in os.listdir(self._IMAGE_FOLDER_FOLDER_PATH) if name.endswith(".png")]:
            image_names.append(file_name.replace(".png", ""))
        for map_coords in MAP_DATA.keys():
            self._custom_assertIn(
                map_coords, 
                image_names,
                msg=f"Image file for map coords '{map_coords}' not found in folder: '{self._IMAGE_FOLDER_FOLDER_PATH}'."
            )

    def _custom_assertIn(self, member, container, msg):
        if member not in container:
            raise AssertionError(msg)

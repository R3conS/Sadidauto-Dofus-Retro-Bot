import os

import cv2

from ._base_option import BaseOption


class Models(BaseOption):

    IMAGE_FOLDER_PATH = "src\\bot\\_states\\in_combat\\_combat_options\\_images\\models"

    def __init__(self):
        super().__init__(
            name="Models",
            on_icon_image_paths=[
                os.path.join(self.IMAGE_FOLDER_PATH, "on.png")
            ],
            off_icon_image_paths=[
                os.path.join(self.IMAGE_FOLDER_PATH, "off.png")
            ]
        )

    def turn_on(self):
        return super()._turn_on(
            is_on=self.is_on,
            get_icon_pos=self._get_icon_pos,
            shrink_turn_bar=True
        )

    def is_on(self):
        return super()._is_on(confidence=0.9, method=cv2.TM_CCORR_NORMED)

    def is_toggle_icon_visible(self):
        return self._get_icon_pos() is not None

    def _get_icon_pos(self):
        return super()._get_icon_pos(confidence=0.89, method=cv2.TM_CCORR_NORMED)

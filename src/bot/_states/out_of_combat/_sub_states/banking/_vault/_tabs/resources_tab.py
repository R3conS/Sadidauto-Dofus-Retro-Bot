import os

from ._base_tab import BaseTab


class ResourcesTab(BaseTab):

    ICONS_FOLDER_PATH = "src\\bot\\_states\\out_of_combat\\_sub_states\\banking\\_vault\\_tabs\\_images\\icons"

    def __init__(self):
        super().__init__(
            name="Resources",
            tab_open_image_paths=[
                os.path.join(self.ICONS_FOLDER_PATH, "tab_resources_open.png"),
                os.path.join(self.ICONS_FOLDER_PATH, "tab_resources_open_2.png")
            ],
            tab_closed_image_paths=[
                os.path.join(self.ICONS_FOLDER_PATH, "tab_resources_closed.png"),
                os.path.join(self.ICONS_FOLDER_PATH, "tab_resources_closed_2.png")
            ],
            forbidden_item_image_paths={}
        )

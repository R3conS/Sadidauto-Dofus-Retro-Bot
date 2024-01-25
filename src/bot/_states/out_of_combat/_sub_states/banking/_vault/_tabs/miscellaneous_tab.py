import os

from src.bot._states.out_of_combat._sub_states.banking._vault._tabs._base_tab import BaseTab


class MiscellaneousTab(BaseTab):

    ICONS_FOLDER_PATH = "src\\bot\\_states\\out_of_combat\\_sub_states\\banking\\_vault\\_tabs\\_images\\icons"
    FORBIDDEN_ITEMS_FOLDER_PATH = "src\\bot\\_states\\out_of_combat\\_sub_states\\banking\\_vault\\_tabs\\_images\\forbidden_items\\misc"

    def __init__(self):
        super().__init__(
            name="Miscellaneous",
            tab_open_image_paths=[
                os.path.join(self.ICONS_FOLDER_PATH, "tab_misc_open.png"),
                os.path.join(self.ICONS_FOLDER_PATH, "tab_misc_open_2.png")
            ],
            tab_closed_image_paths=[
                os.path.join(self.ICONS_FOLDER_PATH, "tab_misc_closed.png"),
                os.path.join(self.ICONS_FOLDER_PATH, "tab_misc_closed_2.png")
            ],
            forbidden_item_image_paths={ # confidence: [image_path, ...]
                0.99: [
                    os.path.join(self.FORBIDDEN_ITEMS_FOLDER_PATH, "recall_potion.png"), 
                    os.path.join(self.FORBIDDEN_ITEMS_FOLDER_PATH, "bonta_potion.png"),
                    os.path.join(self.FORBIDDEN_ITEMS_FOLDER_PATH, "brakmar_potion.png")
                ]
            }
        )

import os

from src.bot._states.out_of_combat._sub_states.banking._vault._tabs._base_tab import BaseTab


class EquipmentTab(BaseTab):

    ICONS_FOLDER_PATH = "src\\bot\\_states\\out_of_combat\\_sub_states\\banking\\_vault\\_tabs\\_images\\icons"

    def __init__(self):
        super().__init__(
            name="Equipment",
            tab_open_image_paths=[
                os.path.join(self.ICONS_FOLDER_PATH, "tab_equipment_open.png"),
                os.path.join(self.ICONS_FOLDER_PATH, "tab_equipment_open_2.png")
            ],
            tab_closed_image_paths=[
                os.path.join(self.ICONS_FOLDER_PATH, "tab_equipment_closed.png"),
                os.path.join(self.ICONS_FOLDER_PATH, "tab_equipment_closed_2.png")
            ],
            forbidden_item_image_paths={}
        )

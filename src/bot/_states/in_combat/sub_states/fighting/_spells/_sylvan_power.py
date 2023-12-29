from ._base_spell import BaseSpell


class SylvanPower(BaseSpell):

    def __init__(self):
        super().__init__(
            name="Sylvan Power",
            image_folder_path="src\\bot\\_states\\in_combat\\sub_states\\fighting\\_spells\\_images\\sylvan_power"
        )

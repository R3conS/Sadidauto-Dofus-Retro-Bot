from ._base_spell import BaseSpell


class Bramble(BaseSpell):

    def __init__(self):
        super().__init__(
            name="Bramble",
            image_folder_path="src\\bot\\_states\\in_combat\\sub_states\\fighting\\_spells\\_images\\bramble"
        )

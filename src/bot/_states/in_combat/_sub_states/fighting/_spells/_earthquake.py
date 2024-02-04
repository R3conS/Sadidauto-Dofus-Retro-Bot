from src.bot._states.in_combat._sub_states.fighting._spells._base_spell import BaseSpell


class Earthquake(BaseSpell):

    def __init__(self):
        super().__init__(
            name="Earthquake",
            image_folder_path="src\\bot\\_states\\in_combat\\_sub_states\\fighting\\_spells\\_images\\earthquake"
        )

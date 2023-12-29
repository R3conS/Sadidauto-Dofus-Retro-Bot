from ._base_spell import BaseSpell


class PoisonedWind(BaseSpell):

    def __init__(self):
        super().__init__(
            name="Poisoned Wind",
            image_folder_path="src\\bot\\_states\\in_combat\\sub_states\\fighting\\_spells\\_images\\poisoned_wind"
        )

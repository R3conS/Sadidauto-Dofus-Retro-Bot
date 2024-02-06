from pyautogui import pixelMatchesColor


class Getter:

    @staticmethod
    def get_data(script: str):
        if "af_" in script:
            return Getter._get_astrub_bank_data()

    @classmethod
    def _get_astrub_bank_data(cls):
        return {
            "bank_map": "4,-16",
            "zaap_map": "4,-19",
            "no_recall_maps": ["4,-16", "4,-17", "4,-18", "4,-19"],
            "enter_coords": (792, 203),
            "exit_coords": (262, 502),
            "npc_image_folder_path": "src\\bot\\_states\\out_of_combat\\_sub_states\\banking\\_vault\\_images\\astrub_banker_npc",
            "is_char_inside_bank": cls.is_char_inside_astrub_bank
        }

    def is_char_inside_astrub_bank():
        return all((
            pixelMatchesColor(10, 587, (0, 0, 0)),
            pixelMatchesColor(922, 587, (0, 0, 0)),
            pixelMatchesColor(454, 90, (0, 0, 0)), 
            pixelMatchesColor(533, 99, (242, 240, 236)),
            pixelMatchesColor(491, 124, (239, 236, 232))
        ))

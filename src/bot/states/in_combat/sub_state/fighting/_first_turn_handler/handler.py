from ._character_finder import Finder as CharacterPosFinder
from ._starting_side_color_getter import Getter as StartingSideColorGetter
from .._fight_preferences.models import Models


class Handler:

    def __init__(self, script: str, character_name: str):
        self.__script = script
        self.__character_name = character_name
        self.__character_pos_finder = CharacterPosFinder(character_name)
        self.__starting_side_color_getter = StartingSideColorGetter(script)

    def handle(self):
        if Models.is_toggle_icon_visible(): # It's invisible after a reconnect.
            result = self.handle_models_toggle_icon_visible()
        else:
            result = self.handle_models_toggle_icon_not_visible()

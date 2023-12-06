from .._character_finder import Finder as CharacterPosFinder
from .._fight_preferences.models import Models
from ..status_enum import Status
from ..data.getter import Getter as FightingDataGetter


class Handler:


    def __init__(self, script: str, character_name: str):
        self.__character_pos_finder = CharacterPosFinder(character_name)
        self.__spell_casting_data = FightingDataGetter.get_data_object(script).get_spell_casting_data()

    def handle(self):
        if Models.is_toggle_icon_visible(): # It's invisible after a reconnect.
            result = self.handle_models_toggle_icon_visible()

    def handle_models_toggle_icon_visible(self):
        if not Models.are_disabled():
            result = Models.disable()
            if (
                result == Status.FAILED_TO_GET_MODELS_TOGGLE_ICON_POS
                or result == Status.TIMED_OUT_WHILE_DISABLING_MODELS
            ):
                return Status.FAILED_TO_DISABLE_MODELS

        character_pos = self.__character_pos_finder.find_by_circles()
        if character_pos == Status.TIMED_OUT_WHILE_WAITING_FOR_INFO_CARD_TO_APPEAR:
            return Status.FAILED_TO_GET_CHARACTER_POS_BY_CIRCLES
        
        # ToDo: link mover and add spellcasting.
        pass

from src.logger import get_logger

log = get_logger()

from src.bot._states.in_combat._sub_states.fighting.fighter import Fighter
from src.bot._states.in_combat._sub_states.preparing.preparer import Preparer
from src.bot._states.in_combat._sub_states.sub_states_enum import State as SubState
from src.bot._states.states_enum import State as MainBotState
from src.utilities.general import load_image
from src.utilities.image_detection import ImageDetection
from src.utilities.screen_capture import ScreenCapture


class Controller:
    
    def __init__(
        self, 
        set_bot_state_callback: callable, 
        script: str, 
        character_name: str,
        disable_spectator_mode: bool = True
    ):
        self._set_main_bot_state_callback = set_bot_state_callback
        image_folder_path = "src\\bot\\_states\\in_combat\\_images"
        self._ap_icon_image = load_image(image_folder_path, "ap_counter_icon.png")
        self._preparer = Preparer(script, disable_spectator_mode)
        self._fighter = Fighter(script, character_name)
        self._fight_counter = 0

    def run(self):
        sub_state = self._determine_sub_state()
        while True:
            if sub_state == SubState.PREPARING:
                self._preparer.prepare()
                sub_state = SubState.FIGHTING

            elif sub_state == SubState.FIGHTING:
                self._fighter.fight()
                self._fight_counter += 1
                log.info(f"Successfully finished fighting. Fight counter: {self._fight_counter}.")
                self._set_main_bot_state_callback(MainBotState.OUT_OF_COMBAT)
                return

    def _determine_sub_state(self):
        if len(
            ImageDetection.find_image(
                haystack=ScreenCapture.custom_area((452, 598, 41, 48)),
                needle=self._ap_icon_image,
                confidence=0.99,
                mask=ImageDetection.create_mask(self._ap_icon_image)
            )
        ) > 0:
            return SubState.FIGHTING
        return SubState.PREPARING

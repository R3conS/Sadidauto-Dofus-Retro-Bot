from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from enum import Enum

from ._sub_states.preparing.preparer import Preparer
from ._sub_states.fighting.fighter import Fighter
from src.utilities import load_image
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture
from src.bot._states.in_combat._status_enum import Status
from src.bot._states.states_enum import State as MainBotState


class Controller:
    
    def __init__(self, set_bot_state_callback: callable, script: str, character_name: str):
        self._set_main_bot_state_callback = set_bot_state_callback
        image_folder_path = "src\\bot\\_states\\in_combat\\_images"
        self._ap_icon_image = load_image(image_folder_path, "sub_state_verifier_1.png")
        self._mp_icon_image = load_image(image_folder_path, "sub_state_verifier_2.png")
        self._preparer = Preparer(script)
        self._fighter = Fighter(script, character_name)
        self._fight_counter = 0

    def run(self):
        sub_state = self._determine_sub_state()
        while True:
            if sub_state == _SubState.PREPARING:
                self._preparer.prepare()
                sub_state = _SubState.FIGHTING

            elif sub_state == _SubState.FIGHTING:
                self._fighter.fight()
                self._fight_counter += 1
                log.info(f"Successfully finished fighting. Fight counter: {self._fight_counter}.")
                self._set_main_bot_state_callback(MainBotState.OUT_OF_COMBAT)
                return

    # ToDo: Check only for the AP image.
    def _determine_sub_state(self):
        ap_icon_rectangle = ImageDetection.find_image(
            haystack=ScreenCapture.custom_area((452, 598, 41, 48)),
            needle=self._ap_icon_image,
            confidence=0.99,
            mask=ImageDetection.create_mask(self._ap_icon_image)
        )
        mp_icon_rectangle = ImageDetection.find_image(
            haystack=ScreenCapture.custom_area((547, 598, 48, 48)),
            needle=self._mp_icon_image,
            confidence=0.98,
            mask=ImageDetection.create_mask(self._mp_icon_image)
        )
        if len(ap_icon_rectangle) > 0 or len(mp_icon_rectangle) > 0:
            return _SubState.FIGHTING
        return _SubState.PREPARING


class _SubState(Enum):

    PREPARING = "PREPARING"
    FIGHTING = "FIGHTING"

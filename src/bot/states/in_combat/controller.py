from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from src.utilities import load_image
from .sub_state.preparing.preparer import Preparer
from .sub_state.fighting.fighter import Fighter
from .sub_state.preparing.status_enum import Status as PreparingStatus
from .sub_state.fighting.status_enum import Status as FightingStatus
from src.bot.main_states_enum import State as MainBotStates
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture


class Controller:
    
    def __init__(self, set_bot_state_callback: callable, script: str, character_name: str):
        self._set_main_bot_state_callback = set_bot_state_callback
        image_folder_path = "src\\bot\\states\\in_combat\\images"
        self._ap_icon_image = load_image(image_folder_path, "sub_state_verifier_1.png")
        self._mp_icon_image = load_image(image_folder_path, "sub_state_verifier_2.png")
        self._preparer = Preparer(script)
        self._fighter = Fighter(script, character_name)
        self._fight_counter = 0

    def run(self):
        sub_state = self._determine_sub_state()
        while True:
            if sub_state == _SubStates.PREPARING:
                status = self._preparer.prepare()
                if status == PreparingStatus.SUCCESSFULLY_FINISHED_PREPARING:
                    sub_state = _SubStates.FIGHTING
                    continue
                elif status == PreparingStatus.FAILED_TO_FINISH_PREPARING:
                    log.error(f"Failed to finish preparing. Attempting to recover ...")
                    self._set_main_bot_state_callback(MainBotStates.RECOVERY)
                    return
                
            elif sub_state == _SubStates.FIGHTING:
                result = self._fighter.fight()
                if result == FightingStatus.SUCCESSFULLY_FINISHED_FIGHTING:
                    self._fight_counter += 1
                    log.info(f"Successfully finished fighting. Fight counter: {self._fight_counter}.")
                    self._set_main_bot_state_callback(MainBotStates.OUT_OF_COMBAT)
                    return
                elif result == FightingStatus.FAILED_TO_FINISH_FIGHTING:
                    log.error(f"Failed to finish fighting. Attempting to recover ...")
                    self._set_main_bot_state_callback(MainBotStates.RECOVERY)
                    return

            elif sub_state == _SubStates.RECOVERY:
                log.error("'In Combat' controller failed to determine its sub state. Attempting to recover ...")
                self._set_main_bot_state_callback(MainBotStates.RECOVERY)
                return

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
            return _SubStates.FIGHTING
        return _SubStates.PREPARING


class _SubStates:

    PREPARING = "PREPARING"
    FIGHTING = "FIGHTING"
    RECOVERY = "RECOVERY"

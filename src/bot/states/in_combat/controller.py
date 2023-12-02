from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import os

import cv2

from .sub_state.preparing.preparer import Preparer
from .sub_state.preparing.status_enum import Status as PreparingStatus
from src.bot.main_states_enum import State as MainBotStates
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture


def _load_image(image_folder_path: str, image_name: str):
    image_path = os.path.join(image_folder_path, image_name)
    if not os.path.exists(image_path) and not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image '{image_name}' not found in '{image_folder_path}'.")
    return cv2.imread(image_path, cv2.IMREAD_UNCHANGED)


class Controller:
    
    def __init__(self, set_bot_state_callback: callable, script: str):
        self.__set_main_bot_state_callback = set_bot_state_callback
        image_folder_path = "src\\bot\\states\\in_combat\\images"
        self.__ap_icon_image = _load_image(image_folder_path, "sub_state_verifier_1.png")
        self.__mp_icon_image = _load_image(image_folder_path, "sub_state_verifier_2.png")
        self.__preparer = Preparer(script)

    def run(self):
        while True:
            sub_state = self.__determine_sub_state()

            if sub_state == _SubStates.PREPARING:
                status = self.__preparer.prepare()
                if status == PreparingStatus.SUCCESSFULLY_FINISHED_PREPARING:
                    continue
                elif status == PreparingStatus.FAILED_TO_FINISH_PREPARING:
                    log.info(f"Failed to finish preparing. Attempting to recover ...")
                    self.__set_main_bot_state_callback(MainBotStates.RECOVERY)
                    return
                
            elif sub_state == _SubStates.FIGHTING:
                log.critical("Fighting is not implemented yet.")
                os._exit(1)

            elif sub_state == _SubStates.RECOVERY:
                log.info("'In Combat' controller failed to determine its sub state. Attempting to recover ...")
                self.__set_main_bot_state_callback(MainBotStates.RECOVERY)
                return

    def __determine_sub_state(self):
        ap_icon_rectangle = ImageDetection.find_image(
            haystack=ScreenCapture.custom_area((452, 598, 41, 48)),
            needle=self.__ap_icon_image,
            confidence=0.99,
            mask=ImageDetection.create_mask(self.__ap_icon_image)
        )
        mp_icon_rectangle = ImageDetection.find_image(
            haystack=ScreenCapture.custom_area((547, 598, 48, 48)),
            needle=self.__mp_icon_image,
            confidence=0.98,
            mask=ImageDetection.create_mask(self.__mp_icon_image)
        )
        if len(ap_icon_rectangle) > 0 or len(mp_icon_rectangle) > 0:
            return _SubStates.FIGHTING
        return _SubStates.PREPARING


class _SubStates:

    PREPARING = "PREPARING"
    FIGHTING = "FIGHTING"
    RECOVERY = "RECOVERY"

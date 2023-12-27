from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter

import cv2
import pyautogui as pyag

from src.utilities import load_image
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture
from src.bot.states.in_combat.sub_state.fighting.status_enum import Status
from .turn_bar import TurnBar


class TacticalMode:
    
    _IMAGE_FOLDER_PATH = "src\\bot\\states\\in_combat\\sub_state\\fighting\\images"
    _TACTICAL_MODE_ON_IMAGE = load_image(_IMAGE_FOLDER_PATH, "tactical_mode_on.png")
    _TACTICAL_MODE_ON_IMAGE_MASK = ImageDetection.create_mask(_TACTICAL_MODE_ON_IMAGE)
    _TACTICAL_MODE_OFF_IMAGE = load_image(_IMAGE_FOLDER_PATH, "tactical_mode_off.png")
    _TACTICAL_MODE_OFF_IMAGE_MASK = ImageDetection.create_mask(_TACTICAL_MODE_OFF_IMAGE)
    _ICON_AREA = (822, 510, 34, 36)

    @classmethod
    def is_on(cls):
        """
        Turn bar must be shrunk for accurate results because sometimes
        the turn indicator arrow blocks the icon.
        """
        return len(
            ImageDetection.find_image(
                haystack=ScreenCapture.custom_area(cls._ICON_AREA),
                needle=cls._TACTICAL_MODE_ON_IMAGE,
                confidence=0.95,
                method=cv2.TM_CCORR_NORMED,
                mask=cls._TACTICAL_MODE_ON_IMAGE_MASK
            )
        ) > 0
    
    @classmethod
    def get_icon_pos(cls):
        images_to_search = [
            (cls._TACTICAL_MODE_ON_IMAGE, cls._TACTICAL_MODE_ON_IMAGE_MASK),
            (cls._TACTICAL_MODE_OFF_IMAGE, cls._TACTICAL_MODE_OFF_IMAGE_MASK)
        ]
        for needle, mask in images_to_search:
            rectangle = ImageDetection.find_image(
                haystack=ScreenCapture.custom_area(cls._ICON_AREA),
                needle=needle,
                confidence=0.98,
                method=cv2.TM_CCORR_NORMED,
                mask=mask
            )
            if len(rectangle) > 0:
                return ImageDetection.get_rectangle_center_point((
                    rectangle[0] + cls._ICON_AREA[0],
                    rectangle[1] + cls._ICON_AREA[1],
                    rectangle[2],
                    rectangle[3]
                ))
        return None
   
    @classmethod
    def turn_on(cls):
        if not TurnBar.is_shrunk():
            result = TurnBar.shrink()
            if result == Status.TIMED_OUT_WHILE_SHRINKING_TURN_BAR:
                return result
            
        if cls.is_on():
            log.info("Tactical mode is already on.")
            return Status.TACTICAL_MODE_IS_ALREADY_ON

        tactical_mode_icon_pos = cls.get_icon_pos()
        if tactical_mode_icon_pos is None:
            log.error("Failed to get tactical mode toggle icon position.")
            return Status.FAILED_TO_GET_TACTICAL_MODE_TOGGLE_ICON_POS

        pyag.moveTo(*tactical_mode_icon_pos)
        pyag.click()

        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if cls.is_on():
                log.info("Successfully turned on tactical mode.")
                return Status.SUCCESSFULLY_TURNED_ON_TACTICAL_MODE
        log.error("Timed out while turning on tactical mode.")
        return Status.TIMED_OUT_WHILE_TURNING_ON_TACTICAL_MODE

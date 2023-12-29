from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter

import cv2
import pyautogui as pyag

from src.utilities import load_image
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture
from src.bot._states.in_combat._status_enum import Status
from .turn_bar import TurnBar


class TacticalMode:
    
    ICON_AREA = (750, 512, 185, 34)
    IMAGE_FOLDER_PATH = "src\\bot\\_states\\in_combat\\_combat_options\\_images"
    TACTICAL_MODE_ON_ICONS = [
        load_image(IMAGE_FOLDER_PATH, "tactical_mode_on.png"),
        load_image(IMAGE_FOLDER_PATH, "tactical_mode_on_2.png")
    ]
    TACTICAL_MODE_ON_ICON_MASKS = [ImageDetection.create_mask(icon) for icon in TACTICAL_MODE_ON_ICONS]
    TACTICAL_MODE_OFF_ICONS = [
        load_image(IMAGE_FOLDER_PATH, "tactical_mode_off.png"),
        load_image(IMAGE_FOLDER_PATH, "tactical_mode_off_2.png")
    ]
    TACTICAL_MODE_OFF_ICON_MASKS = [ImageDetection.create_mask(icon) for icon in TACTICAL_MODE_OFF_ICONS]
    
    @classmethod
    def is_on(cls):
        """
        Turn bar must be shrunk for accurate results because sometimes
        the turn indicator arrow blocks the icon.
        """
        return len(
            ImageDetection.find_images(
                haystack=ScreenCapture.custom_area(cls.ICON_AREA),
                needles=cls.TACTICAL_MODE_ON_ICONS,
                confidence=0.95,
                method=cv2.TM_CCORR_NORMED,
                masks=cls.TACTICAL_MODE_ON_ICON_MASKS
            )
        ) > 0
    
    @classmethod
    def get_icon_pos(cls):
        rectangles = ImageDetection.find_images(
            haystack=ScreenCapture.custom_area(cls.ICON_AREA),
            needles=cls.TACTICAL_MODE_ON_ICONS + cls.TACTICAL_MODE_OFF_ICONS,
            confidence=0.98,
            method=cv2.TM_CCORR_NORMED,
            masks=cls.TACTICAL_MODE_ON_ICON_MASKS + cls.TACTICAL_MODE_OFF_ICON_MASKS
        )
        if len(rectangles) > 0:
            return ImageDetection.get_rectangle_center_point((
                rectangles[0][0] + cls.ICON_AREA[0],
                rectangles[0][1] + cls.ICON_AREA[1],
                rectangles[0][2],
                rectangles[0][3]
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

        icon_pos = cls.get_icon_pos()
        if icon_pos is None:
            log.error("Failed to get tactical mode toggle icon position.")
            return Status.FAILED_TO_GET_TACTICAL_MODE_TOGGLE_ICON_POS

        pyag.moveTo(*icon_pos)
        pyag.click()

        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if cls.is_on():
                log.info("Successfully turned on tactical mode.")
                return Status.SUCCESSFULLY_TURNED_ON_TACTICAL_MODE
        log.error("Timed out while turning on tactical mode.")
        return Status.TIMED_OUT_WHILE_TURNING_ON_TACTICAL_MODE

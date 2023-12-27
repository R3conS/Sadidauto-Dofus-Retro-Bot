from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter

import cv2
import pyautogui as pyag

from .turn_bar import TurnBar
from src.utilities import load_image
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture
from src.bot.states.in_combat.status_enum import Status


class Lock:
    
    _ICON_AREA = (750, 512, 185, 34)
    _IMAGE_FOLDER_PATH = "src\\bot\\states\\in_combat\\sub_state\\_combat_options\\images"
    _FIGHT_LOCK_ON_ICON = load_image(_IMAGE_FOLDER_PATH, "fight_lock_on.png")
    _FIGHT_LOCK_ON_ICON_MASK = ImageDetection.create_mask(_FIGHT_LOCK_ON_ICON)
    _FIGHT_LOCK_OFF_ICON = load_image(_IMAGE_FOLDER_PATH, "fight_lock_off.png")
    _FIGHT_LOCK_OFF_ICON_MASK = ImageDetection.create_mask(_FIGHT_LOCK_OFF_ICON)

    @classmethod
    def is_on(cls):
        """Tactical mode must be on for more accurate results."""
        return len(
            ImageDetection.find_image(
                haystack=ScreenCapture.custom_area(cls._ICON_AREA),
                needle=cls._FIGHT_LOCK_ON_ICON,
                confidence=0.9,
                method=cv2.TM_CCORR_NORMED,
                mask=cls._FIGHT_LOCK_ON_ICON_MASK
            )
        ) > 0

    @classmethod
    def get_icon_pos(cls):
        """Tactical mode must be on for more accurate results."""
        rectangles = ImageDetection.find_images(
            haystack=ScreenCapture.custom_area(cls._ICON_AREA),
            needles=[cls._FIGHT_LOCK_ON_ICON, cls._FIGHT_LOCK_OFF_ICON],
            confidence=0.89,
            method=cv2.TM_CCORR_NORMED,
            masks=[cls._FIGHT_LOCK_ON_ICON_MASK, cls._FIGHT_LOCK_OFF_ICON_MASK]
        )
        if len(rectangles) > 0:
            return ImageDetection.get_rectangle_center_point((
                rectangles[0][0] + cls._ICON_AREA[0],
                rectangles[0][1] + cls._ICON_AREA[1],
                rectangles[0][2],
                rectangles[0][3]
            ))
        return None

    @classmethod
    def turn_on(cls):
        if cls.is_on():
            log.info("Fight lock is already on.")
            return Status.FIGHT_LOCK_IS_ALREADY_ON
        
        icon_pos = cls.get_icon_pos()
        if icon_pos is None:
            log.error("Failed to get fight lock toggle icon position.")
            return Status.FAILED_TO_GET_FIGHT_LOCK_ICON_POS
        
        pyag.moveTo(*icon_pos)
        pyag.click()

        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if cls.is_on():
                log.info("Successfully turned on fight lock.")
                return Status.SUCCESSFULLY_TURNED_ON_FIGHT_LOCK
        log.error("Timed out while turning on fight lock.")
        return Status.TIMED_OUT_WHILE_TURNING_ON_FIGHT_LOCK

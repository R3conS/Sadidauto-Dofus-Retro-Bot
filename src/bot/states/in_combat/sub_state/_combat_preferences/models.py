from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter

import cv2
import pyautogui as pyag

from src.utilities import load_image
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture
from src.bot.states.in_combat.status_enum import Status


class Models:
    
    _ICON_AREA = (750, 512, 185, 34)
    _IMAGE_FOLDER_PATH = "src\\bot\\states\\in_combat\\sub_state\\_combat_options\\images"
    _MODEL_DISABLER_ON_ICON = load_image(_IMAGE_FOLDER_PATH, "model_disabler_on.png")
    _MODEL_DISABLER_ON_ICON_MASK = ImageDetection.create_mask(_MODEL_DISABLER_ON_ICON)
    _MODEL_DISABLER_OFF_ICON = load_image(_IMAGE_FOLDER_PATH, "model_disabler_off.png")
    _MODEL_DISABLER_OFF_ICON_MASK = ImageDetection.create_mask(_MODEL_DISABLER_OFF_ICON)

    @classmethod
    def are_disabled(cls):
        """Tactical mode must be on for more accurate results."""
        return len(
            ImageDetection.find_image(
                haystack=ScreenCapture.custom_area(cls._ICON_AREA),
                needle=cls._MODEL_DISABLER_ON_ICON,
                confidence=0.9,
                method=cv2.TM_CCORR_NORMED,
                mask=cls._MODEL_DISABLER_ON_ICON_MASK
            )
        ) > 0

    @classmethod
    def get_icon_pos(cls):
        """Tactical mode must be on for more accurate results."""
        rectangles = ImageDetection.find_images(
            haystack=ScreenCapture.custom_area(cls._ICON_AREA),
            needles=[cls._MODEL_DISABLER_ON_ICON, cls._MODEL_DISABLER_OFF_ICON],
            confidence=0.89,
            method=cv2.TM_CCORR_NORMED,
            masks=[cls._MODEL_DISABLER_ON_ICON_MASK, cls._MODEL_DISABLER_OFF_ICON_MASK]
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
    def disable(cls):
        icon_pos = cls.get_icon_pos()
        if icon_pos is None:
            log.error("Failed to get models toggle icon position.")
            return Status.FAILED_TO_GET_MODELS_TOGGLE_ICON_POS

        pyag.moveTo(*icon_pos)
        pyag.click()

        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if cls.are_disabled():
                log.info("Successfully disabled models.")
                return Status.SUCCESSFULLY_DISABLED_MODELS
        log.error("Timed out while disabling models.")
        return Status.TIMED_OUT_WHILE_DISABLING_MODELS

    @classmethod
    def is_toggle_icon_visible(cls):
        """Some bug in Dofus causes the icon to disappear after a reconnect."""
        return cls.get_icon_pos() is not None

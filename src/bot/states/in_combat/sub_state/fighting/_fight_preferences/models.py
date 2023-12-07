from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter

import cv2
import pyautogui as pyag

from src.utilities import load_image
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture
from src.bot.states.in_combat.sub_state.fighting.status_enum import Status


class Models:
    
    image_folder_path = "src\\bot\\states\\in_combat\\sub_state\\fighting\\images"
    model_disabler_on_image = load_image(image_folder_path, "model_disabler_on.png")
    model_disabler_on_image_mask = ImageDetection.create_mask(model_disabler_on_image)
    model_disabler_off_image = load_image(image_folder_path, "model_disabler_off.png")
    model_disabler_off_image_mask = ImageDetection.create_mask(model_disabler_off_image)
    icon_area = (853, 514, 30, 34)

    @classmethod
    def are_disabled(cls):
        """Tactical mode must be on for more accurate results."""
        return len(
            ImageDetection.find_image(
                haystack=ScreenCapture.custom_area(cls.icon_area),
                needle=cls.model_disabler_on_image,
                confidence=0.9,
                method=cv2.TM_CCORR_NORMED,
                mask=cls.model_disabler_on_image_mask
            )
        ) > 0

    @classmethod
    def get_icon_pos(cls):
        """Tactical mode must be on for more accurate results."""
        images_to_search = [
            (cls.model_disabler_on_image, cls.model_disabler_on_image_mask),
            (cls.model_disabler_off_image, cls.model_disabler_off_image_mask)
        ]
        for needle, mask in images_to_search:
            rectangle = ImageDetection.find_image(
                haystack=ScreenCapture.custom_area(cls.icon_area),
                needle=needle,
                confidence=0.9,
                method=cv2.TM_CCORR_NORMED,
                mask=mask
            )
            if len(rectangle) > 0:
                return ImageDetection.get_rectangle_center_point((
                    rectangle[0] + cls.icon_area[0],
                    rectangle[1] + cls.icon_area[1],
                    rectangle[2],
                    rectangle[3]
                ))
        return None

    @classmethod
    def disable(cls):
        fight_lock_icon_pos = cls.get_icon_pos()
        if fight_lock_icon_pos is None:
            log.info("Failed to get models toggle icon position.")
            return Status.FAILED_TO_GET_MODELS_TOGGLE_ICON_POS

        pyag.moveTo(*fight_lock_icon_pos)
        pyag.click()

        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if cls.are_disabled():
                log.info("Successfully disabled models.")
                return Status.SUCCESSFULLY_DISABLED_MODELS
        log.info("Timed out while disabling models.")
        return Status.TIMED_OUT_WHILE_DISABLING_MODELS

    @classmethod
    def is_toggle_icon_visible(cls):
        """Some bug in Dofus causes the icon to disappear after a reconnect."""
        return cls.get_icon_pos() is not None

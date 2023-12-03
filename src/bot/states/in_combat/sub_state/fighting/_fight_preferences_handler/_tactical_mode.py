from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter

import cv2
import pyautogui as pyag

from src.utilities import load_image
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture
from src.bot.states.in_combat.sub_state.fighting.status_enum import Status


class TacticalMode:
    
    image_folder_path = "src\\bot\\states\\in_combat\\sub_state\\fighting\\images"
    tactical_mode_on_image = load_image(image_folder_path, "tactical_mode_on.png")
    tactical_mode_on_image_mask = ImageDetection.create_mask(tactical_mode_on_image)
    tactical_mode_off_image = load_image(image_folder_path, "tactical_mode_off.png")
    tactical_mode_off_image_mask = ImageDetection.create_mask(tactical_mode_off_image)
    icon_area = (758, 507, 174, 37)

    @classmethod
    def is_on(cls):
        return len(
            ImageDetection.find_image(
                haystack=ScreenCapture.custom_area(cls.icon_area),
                needle=cls.tactical_mode_on_image,
                confidence=0.98,
                method=cv2.TM_CCORR_NORMED,
                mask=cls.tactical_mode_on_image_mask
            )
        ) > 0
    
    @classmethod
    def get_icon_pos(cls):
        images_to_search = [
            (cls.tactical_mode_on_image, cls.tactical_mode_on_image_mask),
            (cls.tactical_mode_off_image, cls.tactical_mode_off_image_mask)
        ]
        for needle, mask in images_to_search:
            rectangle = ImageDetection.find_image(
                haystack=ScreenCapture.custom_area(cls.icon_area),
                needle=needle,
                confidence=0.98,
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
    def turn_on(cls):
        tactical_mode_icon_pos = cls.get_icon_pos()
        if tactical_mode_icon_pos is None:
            log.info("Failed to get tactical mode toggle icon position.")
            return Status.FAILED_TO_GET_TACTICAL_MODE_TOGGLE_ICON_POS

        pyag.moveTo(*tactical_mode_icon_pos)
        pyag.click()

        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if cls.is_on():
                log.info("Successfully turned on tactical mode.")
                return Status.SUCCESSFULLY_TURNED_ON_TACTICAL_MODE
        log.info("Timed out while turning on tactical mode.")
        return Status.TIMED_OUT_WHILE_TURNING_ON_TACTICAL_MODE

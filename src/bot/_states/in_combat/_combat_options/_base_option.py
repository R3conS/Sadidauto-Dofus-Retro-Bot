from src.logger import get_logger

log = get_logger()

from time import perf_counter

import pyautogui as pyag

from src.bot._exceptions import RecoverableException
from src.bot._states.in_combat._combat_options._turn_bar import TurnBar
from src.utilities.general import load_image_full_path
from src.utilities.image_detection import ImageDetection
from src.utilities.screen_capture import ScreenCapture


class BaseOption:
    
    ICON_AREA = (750, 512, 185, 34)

    def __init__(self, name: str, on_icon_image_paths: list, off_icon_image_paths: list):
        self._name = name.title()
        self._on_icon_images = self._load_images(on_icon_image_paths)
        self._on_icon_image_masks = ImageDetection.create_masks(self._on_icon_images)
        self._off_icon_images = self._load_images(off_icon_image_paths)
        self._off_icon_image_masks = ImageDetection.create_masks(self._off_icon_images)

    def _turn_on(self, is_on: callable, get_icon_pos: callable, shrink_turn_bar: bool):
        log.info(f"Turning on '{self._name}' option ...")
        
        if shrink_turn_bar:
            if not TurnBar.is_shrunk():
                TurnBar.shrink()

        if is_on():
            log.info(f"'{self._name}' option is already on.")
            return

        icon_pos = get_icon_pos()
        if icon_pos is None:
            raise RecoverableException(f"Failed to get '{self._name}' toggle icon position.")

        timeout = 10
        outer_start_time = perf_counter()
        while perf_counter() - outer_start_time < timeout:
            # When character gets disconnected during 'preparing' sub-state,
            # the tactical mode icon will have a green check mark (on) but 
            # the mode won't actually be turned on (Dofus bug). This is why 
            # there are several click attempts so that the icon is unchecked 
            # and checked again.
            pyag.moveTo(*icon_pos)
            pyag.click()
            inner_start_time = perf_counter()
            while perf_counter() - inner_start_time < 2:
                if is_on():
                    log.info(f"Successfully turned on '{self._name}' option.")
                    return

        raise RecoverableException(
            f"Timed out while turning on '{self._name}' option. "
            f"Timeout: {timeout} seconds."
        )

    def _is_on(self, confidence, method):
        return len(
            ImageDetection.find_images(
                haystack=ScreenCapture.custom_area(self.ICON_AREA),
                needles=self._on_icon_images,
                confidence=confidence,
                method=method,
                masks=self._on_icon_image_masks
            )
        ) > 0
    
    def _get_icon_pos(self, confidence, method):
        rectangles = ImageDetection.find_images(
            haystack=ScreenCapture.custom_area(self.ICON_AREA),
            needles=self._on_icon_images + self._off_icon_images,
            confidence=confidence,
            method=method,
            masks=self._on_icon_image_masks + self._off_icon_image_masks
        )
        if len(rectangles) > 0:
            return ImageDetection.get_rectangle_center_point((
                rectangles[0][0] + self.ICON_AREA[0],
                rectangles[0][1] + self.ICON_AREA[1],
                rectangles[0][2],
                rectangles[0][3]
            ))
        return None
   
    @staticmethod
    def _load_images(image_paths: list):
        if not isinstance(image_paths, list):
            raise TypeError("'image_paths' must be of type list.")
        if len (image_paths) == 0:
            raise ValueError("'image_paths' must have at least one element.")
        return [load_image_full_path(path) for path in image_paths]

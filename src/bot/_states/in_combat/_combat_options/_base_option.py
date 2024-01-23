from src.logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from time import perf_counter

import pyautogui as pyag

from ._turn_bar import TurnBar
from src.utilities import load_image_full_path
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture
from src.bot._exceptions import RecoverableException


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

        pyag.moveTo(*icon_pos)
        pyag.click()

        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if is_on():
                log.info(f"Successfully turned on '{self._name}'.")
                return
        
        raise RecoverableException(f"Timed out while turning on '{self._name}'.")

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

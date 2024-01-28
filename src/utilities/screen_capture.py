import cv2 as cv
import numpy as np
import pyautogui


class ScreenCapture:

    GAME_WINDOW_AREA = (0, 0, 933, 755) # With Dofus title bar.
    MAP_AREA = (0, 0, 933, 600) # With Dofus title bar.

    @staticmethod
    def custom_area(region: tuple[int, int, int, int]) -> np.ndarray:
        screenshot = pyautogui.screenshot(region=region)
        screenshot = np.array(screenshot)
        return cv.cvtColor(screenshot, cv.COLOR_RGB2BGR)

    @classmethod
    def game_window(cls) -> np.ndarray:
        return ScreenCapture.custom_area(cls.GAME_WINDOW_AREA)

    @classmethod
    def around_pos(cls, pos: tuple[int, int], radius: int):
        center_x, center_y = pos
        topleft_x = max(center_x - radius, 0)
        topleft_y = max(center_y - radius, 0)
        bottom_right_x = min(center_x + radius, cls.GAME_WINDOW_AREA[2])
        bottom_right_y = min(center_y + radius, cls.GAME_WINDOW_AREA[3])
        return ScreenCapture.custom_area((
            int(topleft_x), 
            int(topleft_y), 
            int(bottom_right_x - topleft_x), 
            int(bottom_right_y - topleft_y)
        ))

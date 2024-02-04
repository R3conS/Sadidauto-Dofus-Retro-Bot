from src.logger import Logger
log = Logger.get_logger()

import os
from datetime import datetime
from functools import wraps
from time import perf_counter

import cv2
import numpy as np
import pyautogui as pyag
from cv2 import imwrite as save_image

from src.utilities.screen_capture import ScreenCapture


def load_image(image_folder_path: str, image_name: str):
    image_path = os.path.join(image_folder_path, image_name)
    if not os.path.exists(image_path):
        raise Exception(f"Path '{image_path}' does not exist.")
    if not os.path.isfile(image_path):
        raise Exception(f"Path '{image_path}' is not a file.")
    return cv2.imread(image_path, cv2.IMREAD_UNCHANGED)


def load_image_full_path(image_path: str):
    if not os.path.exists(image_path):
        raise Exception(f"Path '{image_path}' does not exist.")
    if not os.path.isfile(image_path):
        raise Exception(f"Path '{image_path}' is not a file.")
    return cv2.imread(image_path, cv2.IMREAD_UNCHANGED)


def move_mouse_off_game_area():
    pyag.moveTo(929, 752)


def measure_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = perf_counter()
        result = func(*args, **kwargs)
        end_time = perf_counter()
        print(f"'{func.__name__}' took '{end_time - start_time}' seconds to execute.")
        return result
    return wrapper


def screenshot_game_and_save_to_debug_folder(screenshot_name: str):
    log.info("Screenshotting the game window ... ")
    sc = ScreenCapture.game_window()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
    path = os.path.join(Logger.get_logger_dir_path(), f"{timestamp} - {screenshot_name}.png")
    log.info("Saving the screenshot for debug ... ")
    save_image(path, sc)
    log.info("Screenshot saved!")


def save_image_to_debug_folder(image: np.ndarray, image_name: str):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
    path = os.path.join(Logger.get_logger_dir_path(), f"{timestamp} - {image_name}.png")
    log.info(f"Saving image for debug: '{path}' ... ")
    save_image(path, image)
    log.info("Image saved!")


if __name__ == "__main__":
    save_image_to_debug_folder(ScreenCapture.game_window(), "test")

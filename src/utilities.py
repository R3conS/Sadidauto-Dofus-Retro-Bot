import os

import cv2
import pyautogui as pyag


def load_image(image_folder_path: str, image_name: str):
    image_path = os.path.join(image_folder_path, image_name)
    if not os.path.exists(image_path) and not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image '{image_name}' not found in '{image_folder_path}'.")
    return cv2.imread(image_path, cv2.IMREAD_UNCHANGED)


def move_mouse_off_game_area():
    pyag.moveTo(929, 752)

from src.logger import Logger
log = Logger.get_logger()

import glob
import os

import cv2

from src.bot._states.states_enum import State
from src.utilities.general import load_image_full_path
from src.utilities.image_detection import ImageDetection
from src.utilities.screen_capture import ScreenCapture

IMAGE_FOLDER_PATH = "src\\bot\\_states\\state_determiner\\_images"
AP_COUNTER_IMAGE = load_image_full_path(os.path.join(IMAGE_FOLDER_PATH, "ap_counter_image.png"))
READY_BUTTON_IMAGES = [
    load_image_full_path(path) 
    for path in glob.glob(os.path.join(IMAGE_FOLDER_PATH, "ready_button\\*.png"))
]


def determine_state():
    if (
        len(
            ImageDetection.find_image(
                haystack=ScreenCapture.custom_area((452, 598, 41, 48)), 
                needle=AP_COUNTER_IMAGE,
                confidence=0.99,
                mask=ImageDetection.create_mask(AP_COUNTER_IMAGE)
            )
        ) > 0
        or len(
            ImageDetection.find_images(
                haystack=ScreenCapture.custom_area((678, 507, 258, 91)),
                needles=READY_BUTTON_IMAGES,
                confidence=0.95,
                method=cv2.TM_CCOEFF_NORMED
            )
        ) > 0
    ):
        log.info(f"Determined bot state: {State.IN_COMBAT}.")
        return State.IN_COMBAT
    log.info(f"Determined bot state: {State.OUT_OF_COMBAT}.")
    return State.OUT_OF_COMBAT

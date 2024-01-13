import cv2
import numpy as np

from src.screen_capture import ScreenCapture
from src.ocr.ocr import OCR


class Reader:

    NAME_PLATES_AREA = (0, 526, 984, 43)

    @classmethod
    def screenshot_name_plates(cls):
        return ScreenCapture.custom_area(cls.NAME_PLATES_AREA)

    @classmethod
    def preprocess_screenshot_for_OCR(cls, sc: np.ndarray):
        sc = OCR.resize_image(sc, sc.shape[1] * 10, sc.shape[0] * 10)
        sc = OCR.convert_to_grayscale(sc)
        sc = OCR.binarize_image(sc, 190)
        sc = OCR.invert_image(sc)
        sc = cv2.GaussianBlur(sc, (3, 3), 0)
        return sc

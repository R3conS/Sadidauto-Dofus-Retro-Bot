import os
os.environ["TESSDATA_PREFIX"] = "src\\ocr"

import cv2
import numpy as np
from PIL import Image
from tesserocr import PyTessBaseAPI


class OCR:

    @classmethod
    def get_text_from_image(cls, image: Image.Image | np.ndarray | str):
        if isinstance(image, str):
            if not os.path.exists(image):
                raise FileNotFoundError(f"File {image} not found!")
            return cls._read_text_from_image(Image.open(image))
        elif isinstance(image, Image.Image):
            return cls._read_text_from_image(image)
        elif isinstance(image, np.ndarray):
            return cls._read_text_from_image(Image.fromarray(image))
        raise TypeError(f"Invalid image type: {type(image)}")

    @staticmethod
    def _read_text_from_image(image: Image):
        with PyTessBaseAPI() as api:
            api.SetImage(image)
            return api.GetUTF8Text().strip()

    @staticmethod
    def convert_to_grayscale(image: np.ndarray):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def resize_image(image: np.ndarray, width: int, height: int, interpolation=cv2.INTER_LANCZOS4):
        return cv2.resize(image, (width, height), interpolation)

    @staticmethod
    def invert_image(image: np.ndarray):
        return cv2.bitwise_not(image)

    @staticmethod
    def binarize_image(image: np.ndarray, threshold: int):
        return cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)[1]

    @staticmethod
    def erode_image(image: np.ndarray, kernel_size: int):
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.erode(image, kernel, iterations=1)

    @staticmethod
    def dilate_image(image: np.ndarray, kernel_size: int):
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.dilate(image, kernel, iterations=1)

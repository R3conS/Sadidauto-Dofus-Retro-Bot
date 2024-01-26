import os
os.environ["TESSDATA_PREFIX"] = "src\\utilities\\ocr"

import cv2
import numpy as np
from PIL import Image
from tesserocr import PyTessBaseAPI, RIL


class OCR:

    @classmethod
    def get_text_from_image(
        cls, 
        image: Image.Image | np.ndarray | str,
        with_rectangles: bool = False
    ):
        if not with_rectangles:
            method = cls._read_text_from_image
        else:
            method = cls._read_text_from_image_with_rectangles

        if isinstance(image, str):
            if not os.path.exists(image):
                raise FileNotFoundError(f"File {image} not found!")
            return method(Image.open(image))
        elif isinstance(image, Image.Image):
            return method(image)
        elif isinstance(image, np.ndarray):
            return method(Image.fromarray(image))
        
        raise TypeError(f"Invalid image type: {type(image)}")

    @staticmethod
    def _read_text_from_image(image: Image) -> str:
        with PyTessBaseAPI() as api:
            api.SetImage(image)
            return api.GetUTF8Text().strip()

    @staticmethod
    def _read_text_from_image_with_rectangles(image: Image) -> list[tuple[str, tuple]]:
        with PyTessBaseAPI() as api:
            api.SetImage(image)
            api.Recognize()
            ri = api.GetIterator()
            level = RIL.WORD
            results = []
            while ri:
                if ri.Empty(level):
                    break
                try:
                    box = ri.BoundingBox(level)
                    word = ri.GetUTF8Text(level)
                    results.append((word, (box[0], box[1], box[2] - box[0], box[3] - box[1])))
                except:
                    pass
                ri.Next(level)
            return results

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

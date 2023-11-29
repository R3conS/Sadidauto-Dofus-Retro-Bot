import os
os.environ["TESSDATA_PREFIX"] = "src\\ocr"

import cv2
import numpy as np
from PIL import Image
from paddleocr import PaddleOCR
from tesserocr import PyTessBaseAPI


class OCR:

    @classmethod
    def get_text_from_image(
            cls,
            image: Image.Image | np.ndarray | str,
            ocr_engine: str
        ):
        if isinstance(image, str):
            if not os.path.exists(image):
                raise FileNotFoundError(f"File {image} not found!")
            if ocr_engine == "tesserocr":
                return cls.__read_text_tesserocr(Image.open(image))
            elif ocr_engine == "paddleocr":
                return cls.__read_text_paddleocr(cv2.imread(image, cv2.IMREAD_UNCHANGED))
            else:
                raise ValueError(f"Invalid OCR engine: {ocr_engine}")

        if isinstance(image, Image.Image):
            if ocr_engine == "tesserocr":
                return cls.__read_text_tesserocr(image)
            elif ocr_engine == "paddleocr":
                return cls.__read_text_paddleocr(np.array(image))
            else:
                raise ValueError(f"Invalid OCR engine: {ocr_engine}")

        if isinstance(image, np.ndarray):
            if ocr_engine == "tesserocr":
                return cls.__read_text_tesserocr(Image.fromarray(image))
            elif ocr_engine == "paddleocr":
                return cls.__read_text_paddleocr(image)
            else:
                raise ValueError(f"Invalid OCR engine: {ocr_engine}")
            
        raise TypeError(f"Invalid image type: {type(image)}")

    @staticmethod
    def __read_text_tesserocr(image: Image):
        with PyTessBaseAPI() as api:
            api.SetImage(image)
            return api.GetUTF8Text().strip()

    @staticmethod
    def __read_text_paddleocr(
        image_path: np.ndarray | str,
        lang: str = "en",
        use_angle_cls: bool = False,
        show_log: bool = False
    ):
        if isinstance(image_path, str):
            image_path = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        ocr = PaddleOCR(lang=lang, use_angle_cls=use_angle_cls, show_log=show_log)
        results = ocr.ocr(image_path, cls=use_angle_cls)
        return [result[1][0] for result in results]

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

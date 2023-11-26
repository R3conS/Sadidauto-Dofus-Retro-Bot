import os
os.environ["TESSDATA_PREFIX"] = "src\\tesserocr"

import cv2
import numpy as np
from PIL import Image
from tesserocr import PyTessBaseAPI
from paddleocr import PaddleOCR

from src.detection import Detection


def get_text_from_image(
        image: np.ndarray | str,
        to_grayscale: bool = False,
        resize_to: tuple = None,
        invert: bool = False,
        binarize: int = None,
        erode: int = None,
        dilate: int = None,
        ocr_engine: str = "tesserocr"
    ):
    if isinstance(image, str):
        if not os.path.exists(image):
            raise FileNotFoundError(f"Image path '{image}' does not exist.")
        image = cv2.imread(image, cv2.IMREAD_UNCHANGED)
    if to_grayscale:
        if Detection.get_number_of_channels(image) > 1:
            image = convert_to_grayscale(image)
    if resize_to is not None:
        image = resize_image(image, resize_to[0], resize_to[1])
    if invert:
        image = invert_image(image)
    if binarize is not None:
        image = binarize_image(image, binarize)
    if erode is not None:
        image = erode_image(image, erode)
    if dilate is not None:
        image = dilate_image(image, dilate)
    if ocr_engine == "tesserocr":
        return read_text_tesserocr(Image.fromarray(image))
    elif ocr_engine == "paddleocr":
        return read_text_paddleocr(image)

def convert_to_grayscale(image: np.ndarray):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def resize_image(image: np.ndarray, width: int, height: int, interpolation=cv2.INTER_LANCZOS4):
    return cv2.resize(image, (width, height), interpolation)

def invert_image(image: np.ndarray):
    return cv2.bitwise_not(image)

def binarize_image(image: np.ndarray, threshold: int):
    return cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)[1]

def erode_image(image: np.ndarray, kernel_size: int):
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    return cv2.erode(image, kernel, iterations=1)

def dilate_image(image: np.ndarray, kernel_size: int):
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    return cv2.dilate(image, kernel, iterations=1)

def read_text_tesserocr(image: Image):
    with PyTessBaseAPI() as api:
        api.SetImage(image)
        return api.GetUTF8Text().strip()

def read_text_paddleocr(
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

import os
os.environ["TESSDATA_PREFIX"] = "src\\tesserocr"

from PIL import Image
from tesserocr import PyTessBaseAPI


def get_text_from_image(
        image: Image,
        convert_to_grayscale: bool = False,
        resize_to: tuple = None,
        binarization_threshold_value: int = None,
    ):
    if convert_to_grayscale:
        image = __convert_image_to_grayscale(image)
    if resize_to is not None:
        image = __resize_image(image, resize_to[0], resize_to[1])
    if binarization_threshold_value is not None:
        image = __binarize_image(image, binarization_threshold_value)
    return __get_text_from_image(image)

def __convert_image_to_grayscale(image: Image):
    return image.convert("L")

def __resize_image(image: Image, width, height):
    return image.resize((width, height), Image.LANCZOS)

def __binarize_image(image: Image, threshold):
    return image.point(lambda x: 255 if x > threshold else 0, '1')

def __get_text_from_image(image: Image):
    with PyTessBaseAPI() as api:
        api.SetImage(image)
        return api.GetUTF8Text().strip()

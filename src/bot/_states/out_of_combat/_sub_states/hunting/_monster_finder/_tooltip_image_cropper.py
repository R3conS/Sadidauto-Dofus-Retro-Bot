import cv2
import numpy as np

from src.utilities.general import load_image_full_path
from src.utilities.ocr.ocr import OCR


class ImageCroper:

    def __init__(self, image: np.ndarray | str):
        if isinstance(image, str):
            image = load_image_full_path(image)
        self._original_image = image
        self._preprocessed_image = self._preprocess_image(image)
        self._top_line_coords = self._find_top_line_start_coords()
        self._bottom_line_coords = self._find_bottom_line_start_coords()
        self._left_line_coords = self._find_left_line_start_coords()
        self._right_line_coords = self._find_right_line_start_coords()

    def get_cropped_image(self):
        return self._crop_image()

    def _find_top_line_start_coords(self):
        """Returns top line starting coordinates (y, x)."""
        for x in range(self._preprocessed_image.shape[1]):
            if self._preprocessed_image[0, x] == 255:
                return 0, x

    def _find_bottom_line_start_coords(self):
        """Returns bottom line starting coordinates (y, x)."""
        first_row_white_pixel_count = self._count_white_pixels_on_row(self._preprocessed_image, 0)
        for y in range(self._preprocessed_image.shape[0] - 1, -1, -1):
            current_row_white_pixel_count = self._count_white_pixels_on_row(self._preprocessed_image, y)
            if current_row_white_pixel_count == first_row_white_pixel_count:
                return y, self._top_line_coords[1]
            elif current_row_white_pixel_count > first_row_white_pixel_count - 10:
                self._top_line_coords = (self._top_line_coords[0], self._find_first_white_pixel_on_row(y))
                return y, self._top_line_coords[1]
        return None

    def _find_left_line_start_coords(self):
        return self._top_line_coords
    
    def _find_right_line_start_coords(self):
        return (
            min(
                self._count_white_pixels_on_row(self._preprocessed_image, self._top_line_coords[0]), # Top line
                self._count_white_pixels_on_row(self._preprocessed_image, self._bottom_line_coords[0]) # Bottom line
            ),
            self._top_line_coords[1]
        )

    def _find_first_white_pixel_on_row(self, row: int):
        for x in range(self._preprocessed_image.shape[1]):
            if self._preprocessed_image[row, x] == 255:
                return x
        return None

    def _crop_image(self):
        return self._original_image[
            self._top_line_coords[0]:self._bottom_line_coords[0],
            self._bottom_line_coords[1]:self._original_image.shape[1]
        ]

    @staticmethod
    def _preprocess_image(image: np.ndarray | str):
        if isinstance(image, str):
            image = load_image_full_path(image)
        image = OCR.convert_to_grayscale(image)
        image = OCR.binarize_image(image, 80)
        image = OCR.erode_image(image, 4)
        image = OCR.invert_image(image)
        return image

    @staticmethod
    def _count_white_pixels_on_row(image: np.ndarray, row: int):
        return np.sum(image[row] == 255)


if __name__ == "__main__":
    from time import sleep
    tooltip = ImageCroper("tooltip1.png").get_cropped_image()
    cv2.imshow("cropped", tooltip)
    cv2.waitKey(0)

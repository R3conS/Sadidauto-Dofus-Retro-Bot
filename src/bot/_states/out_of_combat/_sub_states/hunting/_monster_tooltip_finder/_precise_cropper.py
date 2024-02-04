import cv2
import numpy as np

from src.utilities.general import load_image_full_path
from src.utilities.ocr.ocr import OCR


class PreciseCropper:

    def __init__(self, rough_tooltip_image: np.ndarray | str):
        if isinstance(rough_tooltip_image, str):
            rough_tooltip_image = load_image_full_path(rough_tooltip_image)
        self._original_image = rough_tooltip_image
        self._preprocessed_image = self._preprocess_image(rough_tooltip_image)
        self._top_line_start_coords = self._find_top_line_start_coords()
        self._bottom_line_start_coords = self._find_bottom_line_start_coords()
        self._left_line_start_coords = self._find_left_line_start_coords()
        self._right_line_start_coords = self._find_right_line_start_coords()
        self.crop_area = self._calculate_crop_area()
        self.tooltip = self._crop(rough_tooltip_image, self.crop_area)

    def _find_top_line_start_coords(self):
        """Returns top line starting coordinates (y, x)."""
        return 0, self._find_first_white_pixel_on_row(0)

    def _find_bottom_line_start_coords(self):
        """Returns bottom line starting coordinates (y, x)."""
        first_row_white_pixel_count = self._count_white_pixels_on_row(self._preprocessed_image, 0)
        for y in range(self._preprocessed_image.shape[0] - 1, -1, -1):
            current_row_white_pixel_count = self._count_white_pixels_on_row(self._preprocessed_image, y)
            if current_row_white_pixel_count >= first_row_white_pixel_count - 3:
                x = max(self._top_line_start_coords[1],  self._find_first_white_pixel_on_row(y))
                self._top_line_start_coords = (self._top_line_start_coords[0], x)
                return y, x
        return None

    def _find_left_line_start_coords(self):
        """Returns left line starting coordinates (y, x)."""
        return self._top_line_start_coords
    
    def _find_right_line_start_coords(self):
        """Returns right line starting coordinates (y, x)."""
        top_line_length = self._count_white_pixels_on_row(self._preprocessed_image, self._top_line_start_coords[0])
        bottom_line_length = self._count_white_pixels_on_row(self._preprocessed_image, self._bottom_line_start_coords[0])
        return (
            self._top_line_start_coords[0],
            self._top_line_start_coords[1] + min(top_line_length, bottom_line_length)
        )

    def _find_first_white_pixel_on_row(self, row: int):
        for x in range(self._preprocessed_image.shape[1]):
            if self._preprocessed_image[row, x] == 255:
                return x
        return None

    def _calculate_crop_area(self):
        """Returns the crop area (x, y, w, h)."""
        return (
            self._top_line_start_coords[1],
            self._top_line_start_coords[0],
            self._right_line_start_coords[1] - self._top_line_start_coords[1],
            self._bottom_line_start_coords[0] - self._top_line_start_coords[0]
        )

    @staticmethod
    def _crop(rough_tooltip_image, crop_area: tuple[int, int, int, int]):
        return rough_tooltip_image[
            crop_area[1]: crop_area[1] + crop_area[3],
            crop_area[0]: crop_area[0] + crop_area[2]
        ]

    @staticmethod
    def _preprocess_image(image: np.ndarray | str):
        if isinstance(image, str):
            image = load_image_full_path(image)
        image = OCR.convert_to_grayscale(image)
        image = OCR.binarize_image(image, 65)
        image = OCR.erode_image(image, 3)
        image = OCR.invert_image(image)
        return image

    @staticmethod
    def _count_white_pixels_on_row(image: np.ndarray, row: int):
        return np.sum(image[row] == 255)


if __name__ == "__main__":
    images = [
        "tooltip_0.png",
        "tooltip_1.png",
        "tooltip_2.png",
        "tooltip0.png",
        "tooltip1.png",
        "tooltip2.png"
    ]
    for image in images:
        cropper = PreciseCropper(image)
        print(cropper._bottom_line_start_coords)
        print(cropper._calculate_crop_area())
        print(f"Top line start coords: {cropper._top_line_start_coords}")
        print(f"Bottom line start coords: {cropper._bottom_line_start_coords}")
        print(f"Left line start coords: {cropper._left_line_start_coords}")
        print(f"Right line start coords: {cropper._right_line_start_coords}")
        cv2.imshow("tooltip", cropper.tooltip)
        cv2.waitKey(0)

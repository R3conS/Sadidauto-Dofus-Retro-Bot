import os

import cv2
import numpy as np


class Detection:

    @classmethod
    def find_image(
            cls,
            haystack: np.ndarray | str,
            needle: np.ndarray | str,
            confidence: float = 0.9,
            method: int = cv2.TM_CCORR_NORMED,
            mask: np.ndarray = None,
            remove_alpha_channels: bool = True,
            get_best_match_only: bool = True
        ) -> tuple[int, int, int, int] | list[tuple[int, int, int, int]] | list:
        """Get location of the best match of needle image in haystack image."""
        # Make sure correct method is selected when mask is given
        if mask is not None and method not in [cv2.TM_SQDIFF, cv2.TM_CCORR_NORMED]:
            raise ValueError("Mask is allowed only with TM_SQDIFF and TM_CCORR_NORMED match methods.")
        
        # Read images if they are given as paths
        if isinstance(haystack, str):
            if not os.path.exists(haystack):
                raise FileNotFoundError(f"Haystack image path '{haystack}' does not exist.")
            haystack = cv2.imread(haystack, cv2.IMREAD_UNCHANGED)
        if isinstance(needle, str):
            if not os.path.exists(needle):
                raise FileNotFoundError(f"Needle image path '{needle}' does not exist.")
            needle = cv2.imread(needle, cv2.IMREAD_UNCHANGED)

        # Remove alpha channels if needed
        if remove_alpha_channels:
            if cls.get_number_of_channels(haystack) == 4:
                haystack = haystack[:, :, :3]
            if cls.get_number_of_channels(needle) == 4:
                needle = needle[:, :, :3]

        # Make sure number of channels in both images is the same
        h_channels = cls.get_number_of_channels(haystack)
        n_channels = cls.get_number_of_channels(needle)
        if h_channels != n_channels:
            raise ValueError(
                f"Number of channels in haystack and needle images do not match. "
                f"Haystack = {h_channels}, needle = {n_channels}."
            )
        
        # Get locations according to confidence level
        result = cv2.matchTemplate(haystack, needle, method, mask=mask)
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            if method == cv2.TM_SQDIFF:
                locations = np.where(result <= np.min(result))
            else:
                locations = np.where(result <= 1 - confidence)
        else:
            locations = np.where(result >= confidence)

        locations = list(zip(*locations[::-1]))  # Create a list of (x, y) tuples
        if len(locations) > 0:
            if not get_best_match_only:
                return [(loc[0], loc[1], needle.shape[1], needle.shape[0]) for loc in locations]
            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                best_match_index = np.argmin([result[loc[1], loc[0]] for loc in locations])
            else:
                best_match_index = np.argmax([result[loc[1], loc[0]] for loc in locations])
            return locations[best_match_index][0], locations[best_match_index][1], needle.shape[1], needle.shape[0]
        return locations

    @classmethod
    def find_images(
            cls,
            haystack: np.ndarray | str,
            needles: list[np.ndarray | str],
            confidence: float = 0.9837,
            method: int = cv2.TM_CCORR_NORMED,
            masks: list[np.ndarray] = None,
            remove_alpha_channels: bool = True,
        ) -> list[tuple[int, int, int, int]] | list:
        """Get locations of the best matches of needle images in haystack image.""" 
        # Make sure number of masks matches number of needles
        if masks is not None:        
            if len(needles) != len(masks):
                raise ValueError("Number of masks must match number of needles.")

        # Read images if they are given as paths
        if isinstance(haystack, str):
            if not os.path.exists(haystack):
                raise FileNotFoundError(f"Haystack image path '{haystack}' does not exist.")
            haystack = cv2.imread(haystack, cv2.IMREAD_UNCHANGED)
        for i, needle in enumerate(needles):
            if isinstance(needle, str):
                if not os.path.exists(needle):
                    raise FileNotFoundError(f"Needle image path '{needle}' does not exist.")
                needles[i] = cv2.imread(needle, cv2.IMREAD_UNCHANGED)

        matches = []
        for i, needle in enumerate(needles):
            result = cls.find_image(
                haystack=haystack,
                needle=needle,
                confidence=confidence,
                method=method,
                mask=masks[i] if masks is not None else None,
                remove_alpha_channels=remove_alpha_channels,
            )
            if len(result) > 0:
                matches.append(result)
        return matches

    @staticmethod
    def create_mask(image: np.ndarray | str):
        if isinstance(image, str):
            if not os.path.exists(image):
                raise FileNotFoundError(f"Image path '{image}' does not exist.")
            image = cv2.imread(image, cv2.IMREAD_UNCHANGED)
        if Detection.get_number_of_channels(image) < 4:
            raise ValueError("Provided image doesn't have an alpha channel.")
        _, mask = cv2.threshold(image[..., 3], 127, 255, cv2.THRESH_BINARY)
        return mask

    @staticmethod
    def create_masks(images: list[np.ndarray | str]):
        masks = []
        for image in images:
            if isinstance(image, str):
                if not os.path.exists(image):
                    raise FileNotFoundError(f"Image path '{image}' does not exist.")
                image = cv2.imread(image, cv2.IMREAD_UNCHANGED)
            masks.append(Detection.create_mask(image))
        return masks

    @staticmethod
    def get_number_of_channels(image: np.ndarray):
        if len(image.shape) == 2:
            return 1
        return image.shape[-1]

    @staticmethod
    def get_rectangle_center_point(x_y_w_h: tuple[int, int, int, int]):
        return (
            int(x_y_w_h[0] + (x_y_w_h[2] / 2)),
            int(x_y_w_h[1] + (x_y_w_h[3] / 2))
        )

    @staticmethod
    def draw_rectangle(
        image_to_draw_on: np.ndarray, 
        x_y_w_h: tuple[int, int, int, int], 
        color: tuple[int, int, int] = (0, 255, 0),
        thickness: int = 2,
        line_type: int = cv2.LINE_4
    ):
        return cv2.rectangle(
            image_to_draw_on,
            (x_y_w_h[0], x_y_w_h[1]),
            (x_y_w_h[0] + x_y_w_h[2], x_y_w_h[1] + x_y_w_h[3]),
            color,
            thickness,
            line_type
        )

    @staticmethod
    def draw_marker(
        image_to_draw_on: np.ndarray,
        x_y: tuple[int, int],
        color: tuple[int, int, int] = (0, 255, 0),
        marker_type: int = cv2.MARKER_CROSS,
        marker_size: int = 10,  
        thickness: int = 2,
        line_type: int = cv2.LINE_4
    ):
        return cv2.drawMarker(
            image_to_draw_on,
            x_y,
            color,
            marker_type,
            marker_size,
            thickness,
            line_type
        )

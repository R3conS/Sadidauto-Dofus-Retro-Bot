import cv2
import numpy as np

from src.utilities.image_detection import ImageDetection
from src.utilities.ocr.ocr import OCR
import math
from src.utilities.general import load_image_full_path
from src.utilities.screen_capture import ScreenCapture


class Finder:

    @classmethod
    def find_tooltip_rectangle(cls, tooltip_image: np.ndarray):
        rectangle_lines = cls._find_intersecting_rectangle_lines(tooltip_image)
        intersections = cls._calculate_all_intersections(rectangle_lines)
        corner_intersections = cls._get_corner_intersections(intersections, tooltip_image.shape[1], tooltip_image.shape[0])
        top_left_and_bottom_right_corners = cls._get_top_left_and_bottom_right_corners(corner_intersections)
        rectangle = cls._calculate_rectangle(top_left_and_bottom_right_corners)
        return rectangle

    @staticmethod
    def _calculate_all_intersections(line_points):
        intersections = []
        for i in range(len(line_points)):
            for j in range(i+1, len(line_points)):
                x1, y1, x2, y2 = line_points[i]
                x3, y3, x4, y4 = line_points[j]
                denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
                if denominator == 0:
                    continue
                px = ((x1*y2 - y1*x2)*(x3 - x4) - (x1 - x2)*(x3*y4 - y3*x4)) / denominator
                py = ((x1*y2 - y1*x2)*(y3 - y4) - (y1 - y2)*(x3*y4 - y3*x4)) / denominator
                intersections.append((px, py))
        return intersections

    @classmethod
    def _get_corner_intersections(cls, intersections: list, image_w, image_h, group_threshold=30):
        normalized_intersections = cls._normalize_intersections_to_positive(intersections)
        in_bounds_intersections = cls._remove_out_of_bounds_intersections(normalized_intersections, image_w, image_h)
        sorted_intersections = sorted(in_bounds_intersections)
        intersection_clusters = cls._group_intersections_into_clusters(sorted_intersections, group_threshold)
        largest_cluster_points = cls._get_largest_point_per_cluster(intersection_clusters)
        return largest_cluster_points

    @staticmethod
    def _normalize_intersections_to_positive(intersections: list[tuple[int, int]]):
        return [(int(round(abs(x))), int(round(abs(y)))) for (x, y) in intersections]

    @staticmethod
    def _remove_out_of_bounds_intersections(intersections: list[tuple[int, int]], max_w: int, max_h: int):
        in_bounds_intersections = []
        for (x, y) in intersections:
            if x <= max_w and y <= max_h:
                in_bounds_intersections.append((x, y))
        return in_bounds_intersections

    @classmethod
    def _group_intersections_into_clusters(cls, intersections: list[tuple[int, int]], group_threshold: int):
        intersection_clusters = []
        for intersection in intersections:
            for cluster in intersection_clusters:
                if any(cls._distance_between_points(cluster_point, intersection) <= group_threshold for cluster_point in cluster):
                    cluster.append(intersection)
                    break
            else:
                intersection_clusters.append([intersection])
        return intersection_clusters

    @staticmethod
    def _get_largest_point_per_cluster(clusters: list[list[tuple[int, int]]]):
        merged_clusters = []
        for cluster in clusters:
            max_x = max(point[0] for point in cluster)
            max_y = max(point[1] for point in cluster)
            merged_clusters.append((max_x, max_y))
        return merged_clusters

    @staticmethod
    def _find_all_lines(image: np.ndarray, aperture_size: int) -> list[tuple[int, int, int, int]]:
        """Find all lines in the image and return each line as (x1, y1, x2, y2)."""
        if len(image.shape) >= 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(image, 50, 150, apertureSize=aperture_size)
        lines = cv2.HoughLines(edges, 1, np.pi/180, 60)

        if lines is None:
            return []
        
        line_points = []
        for line in lines:
            rho, theta = line[0]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(round(x0 + 1000 * (-b)))
            y1 = int(round(y0 + 1000 * (a)))
            x2 = int(round(x0 - 1000 * (-b)))
            y2 = int(round(y0 - 1000 * (a)))
            line_points.append((x1, y1, x2, y2))
            
        return line_points

    @classmethod
    def _find_intersecting_rectangle_lines(cls, image: np.ndarray | str):
        """
        Find lines that intersect to form a rectangle in the middle of them.
        The rectangle is the tooltip.
        """
        config = {"binarization_thresholds": [70, 50], "aperture_sizes": [5, 3]}
        original_image = image.copy()
        for i in range(len(config["binarization_thresholds"])):
            image = cls._preprocess_image(original_image, config["binarization_thresholds"][i])
            for j in range(len(config["aperture_sizes"])):
                all_line_points = cls._find_all_lines(image, config["aperture_sizes"][j])
                if len(all_line_points) == 0:
                    continue
                top = cls._get_most_top_line(all_line_points, image.shape)
                bottom = cls._get_most_bottom_line(all_line_points, image.shape)
                right = cls._get_most_right_line(all_line_points, image.shape)
                left = cls._get_most_left_line(all_line_points, image.shape)
                if top != bottom and left != right:
                    return [top, bottom, right, left]
        return None

    @classmethod
    def _get_most_bottom_line(cls, lines, image_shape: tuple[int, int]):
        highest_line = None
        highest_y = float('-inf')
        for line in lines:
            _, y1, _, y2 = line
            if cls._is_y_out_of_bounds(y1, image_shape[0]) or cls._is_y_out_of_bounds(y2, image_shape[0]):
                continue
            if not cls._are_components_within_deviation_threshold(y1, y2, 40):
                continue
            max_y = max(y1, y2)
            if max_y > highest_y:
                highest_line = line
                highest_y = max_y
        return highest_line

    @classmethod
    def _get_most_right_line(cls, lines, image_shape: tuple[int, int]):
        highest_line = None
        highest_x = float('-inf')
        for line in lines:
            x1, _, x2, _ = line
            if cls._is_x_out_of_bounds(x1, image_shape[1]) or cls._is_x_out_of_bounds(x2, image_shape[1]):
                continue
            if not cls._are_components_within_deviation_threshold(x1, x2, 40):
                continue
            max_x = max(x1, x2)
            if max_x > highest_x:
                highest_line = line
                highest_x = max_x
        return highest_line

    @classmethod
    def _get_most_left_line(cls, lines, image_shape: tuple[int, int]):
        lowest_line = None
        lowest_x = float('inf')
        for line in lines:
            x1, _, x2, _ = line
            if cls._is_x_out_of_bounds(x1, image_shape[1]) or cls._is_x_out_of_bounds(x2, image_shape[1]):
                continue
            if not cls._are_components_within_deviation_threshold(x1, x2, 40):
                continue
            min_x = min(x1, x2)
            if min_x < lowest_x:
                lowest_line = line
                lowest_x = min_x
        return lowest_line

    @classmethod
    def _get_most_top_line(cls, lines, image_shape: tuple[int, int]):
        lowest_line = None
        lowest_y = float('inf')
        for line in lines:
            _, y1, _, y2 = line
            if cls._is_y_out_of_bounds(y1, image_shape[0]) or cls._is_y_out_of_bounds(y2, image_shape[0]):
                continue
            if not cls._are_components_within_deviation_threshold(y1, y2, 40):
                continue
            min_y = min(y1, y2)
            if min_y < lowest_y:
                lowest_line = line
                lowest_y = min_y
        return lowest_line

    @staticmethod
    def _get_top_left_and_bottom_right_corners(points: list[tuple[int, int]]):
        min_x = min(point[0] for point in points)
        min_y = min(point[1] for point in points)
        max_x = max(point[0] for point in points)
        max_y = max(point[1] for point in points)
        return (min_x, min_y), (max_x, max_y)

    @staticmethod
    def _preprocess_image(image: np.ndarray | str, binarization_threshold):
        if isinstance(image, str):
            image = load_image_full_path(image)
        image = OCR.convert_to_grayscale(image)
        image = OCR.binarize_image(image, binarization_threshold)
        image = OCR.invert_image(image)
        return image

    @staticmethod
    def _is_y_out_of_bounds(y, max_y):
        return y > max_y or y < 0

    @staticmethod
    def _is_x_out_of_bounds(x, max_x):
        return x > max_x or x < 0

    @staticmethod
    def _are_components_within_deviation_threshold(component1, component2, threshold):
        """Bigger `threshold` means a less linear line. 0 is fully linear."""
        return abs(component1 - component2) <= threshold

    @staticmethod
    def _distance_between_points(point1, point2):
        return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

    @staticmethod
    def _calculate_rectangle(corners) -> tuple[int, int, int, int]:
        """Returns (x, y, w, h)."""
        return (
            corners[0][0],
            corners[0][1],
            corners[1][0] - corners[0][0],
            corners[1][1] - corners[0][1]
        )


if __name__ == "__main__":
    images = [
        "test_1.png",
        "test_2.png",
        "test_3.png",
        "test_4.png",
        "test_5.png",
        "test_6.png",
        "test_7.png",
        "test_8.png",
    ]

    for image_path in images:
        image = cv2.imread(f"{image_path}")
        image_color = image.copy()

        rectangle = Finder.find_tooltip_rectangle(image)
        image_color = ImageDetection.draw_rectangle(image_color, rectangle)

        # cv2.imshow("haystack_colored", image_color)
        # cv2.waitKey(0)

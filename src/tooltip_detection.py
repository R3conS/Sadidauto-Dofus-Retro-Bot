import cv2
import numpy as np

from src.utilities.image_detection import ImageDetection
from src.utilities.ocr.ocr import OCR
import math

def preprocess_image(image: np.ndarray):
    image = OCR.convert_to_grayscale(image)
    image = OCR.binarize_image(image, 70)
    image = OCR.invert_image(image)
    return image

def find_line_points(image: np.ndarray, threshold=65):
    if len(image.shape) >= 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(image, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi/180, threshold)

    global color_img

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
        color_img = cv2.line(color_img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        line_points.append((x1, y1, x2, y2))

    cv2.imshow("houghLines", color_img)
    # cv2.waitKey(0)

    return line_points

def calculate_all_intersections(line_points):
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

def get_corner_intersections(intersections: list, image_w, image_h, group_threshold=30):
    normalized_intersections = normalize_intersections_to_positive(intersections)
    in_bounds_intersections = remove_out_of_bounds_intersections(normalized_intersections, image_w, image_h)
    sorted_intersections = sorted(in_bounds_intersections)
    intersection_clusters = group_intersections_into_clusters(sorted_intersections, group_threshold)
    largest_cluster_points = get_largest_point_per_cluster(intersection_clusters)
    return largest_cluster_points

def normalize_intersections_to_positive(intersections):
    return [(int(round(abs(x))), int(round(abs(y)))) for (x, y) in intersections]

def remove_out_of_bounds_intersections(intersections, max_w, max_h):
    in_bounds_intersections = []
    for (x, y) in intersections:
        if x <= max_w and y <= max_h:
            in_bounds_intersections.append((x, y))
    return in_bounds_intersections

def group_intersections_into_clusters(intersections, group_threshold):
    intersection_clusters = []
    for intersection in intersections:
        for cluster in intersection_clusters:
            if any(distance_between_points(cluster_point, intersection) <= group_threshold for cluster_point in cluster):
                cluster.append(intersection)
                break
        else:
            intersection_clusters.append([intersection])
    return intersection_clusters

def get_largest_point_per_cluster(clusters):
    merged_clusters = []
    for cluster in clusters:
        max_x = max(point[0] for point in cluster)
        max_y = max(point[1] for point in cluster)
        merged_clusters.append((max_x, max_y))
    return merged_clusters

def distance_between_points(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

def find_top_left_and_bottom_right_corners(points):
    min_x = min(point[0] for point in points)
    min_y = min(point[1] for point in points)
    max_x = max(point[0] for point in points)
    max_y = max(point[1] for point in points)
    return (min_x, min_y), (max_x, max_y)

def calculate_rectangle(corners):
    return (
        corners[0][0],
        corners[0][1],
        corners[1][0] - corners[0][0],
        corners[1][1] - corners[0][1]
    )

def get_tooltip_rectangle(image: np.ndarray, threshold=65):
    line_points = find_line_points(image, threshold)
    intersections = calculate_all_intersections(line_points)
    print(f"\nAll intersections: {intersections}")
    intersections = get_corner_intersections(intersections, image.shape[1], image.shape[0])
    print(f"Corner intersections: {intersections}")
    corners = find_top_left_and_bottom_right_corners(intersections)
    print(f"Top left/bottom right corners: {corners}")
    rectangle = calculate_rectangle(corners)
    return rectangle


color_img = None

def main():
    # - Some examples have left, right but no bottom or top lines. Can 
    # make the bottom line the same length as the top line. This
    # also happens with the left and right lines.
    # - If there is no top line but there is a bottom line, some how
    # find the top line and make it same length as bottom line.
    images = [
        # "test_1.png",
        "test_2.png",
        # "test_3.png",
        # "test_4.png",
        # "test_5.png",
        # "test_6.png",
        # "test_7.png",
        # "test_8.png",
    ]

    for image_path in images:
        image = cv2.imread(f"{image_path}")
        image_color = image.copy()
        global color_img
        color_img = image_color.copy()

        image = preprocess_image(image)

        cv2.imshow("haystack_pre", image)

        rectangle = get_tooltip_rectangle(image, threshold=60)
        image_color = ImageDetection.draw_rectangle(image_color, rectangle)

        cv2.imshow("haystack_colored", image_color)
        cv2.waitKey(0)


if __name__ == "__main__":
    main()

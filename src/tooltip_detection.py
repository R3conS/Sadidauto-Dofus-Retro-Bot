import cv2
import numpy as np

from src.utilities.image_detection import ImageDetection
from src.utilities.ocr.ocr import OCR


def preprocess_image(image: np.ndarray):
    image = OCR.convert_to_grayscale(image)
    image = OCR.binarize_image(image, 80)
    image = OCR.invert_image(image)
    return image

def find_line_points(image: np.ndarray, threshold=65):
    if len(image.shape) >= 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(image, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi/180, threshold)
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

def parse_intersections(intersections: list, image_w, image_h, group_threshold=30):
    intersections = [(int(round(abs(x))), int(round(abs(y)))) for (x, y) in intersections]
    for (x, y) in intersections:
        if x > image_w or y > image_h:
            intersections.remove((x, y))
    intersections = sorted(intersections)

    grouped_intersections = [intersections[0]]
    for i in range(1, len(intersections)):
        if max(
            abs(grouped_intersections[-1][0] - intersections[i][0]), 
            abs(grouped_intersections[-1][1] - intersections[i][1])
        ) > group_threshold:
            grouped_intersections.append(intersections[i])

    return grouped_intersections

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

def get_tooltip_rectangle(image: np.ndarray):
    line_points = find_line_points(image)
    intersections = calculate_all_intersections(line_points)
    intersections = parse_intersections(intersections, image.shape[1], image.shape[0])
    corners = find_top_left_and_bottom_right_corners(intersections)
    rectangle = calculate_rectangle(corners)
    return rectangle

def main():
    image = cv2.imread("test_3_preprocessed.png")
    image_color = image.copy()
    image = preprocess_image(image)

    rectangle = get_tooltip_rectangle(image)
    image_color = ImageDetection.draw_rectangle(image_color, rectangle)

    cv2.imshow("img_color", image_color)
    cv2.waitKey(0)


if __name__ == "__main__":
    main()

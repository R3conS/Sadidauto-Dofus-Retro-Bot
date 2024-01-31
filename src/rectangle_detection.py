from time import perf_counter, sleep

import cv2
import numpy as np

from src.utilities.image_detection import ImageDetection
from src.utilities.ocr.ocr import OCR
from src.utilities.screen_capture import ScreenCapture


def expand_right_from_point(image: np.ndarray, start_point: tuple[int, int], processed_points=None):
    if processed_points is None:
        processed_points = set()

    start_x, start_y = start_point
    for x in range(start_x, image.shape[1]):
        if image[start_y, x] == 255 and (start_y, x) in processed_points:
            if x == image.shape[1] - 1:
                return x, start_y
            continue
        elif image[start_y, x] == 0:
            return x - 1, start_y
        elif image[start_y, x] == 255 and x == image.shape[1] - 1:
            return x, start_y
        elif (start_x, x + 1) in processed_points:
            return x, start_y

    return None

def expand_down_from_point(image: np.ndarray, start_point: tuple[int, int], processed_points=None):
    if processed_points is None:
        processed_points = set()

    start_x, start_y = start_point
    for y in range(start_y, image.shape[0]):
        if (y, start_x) in processed_points and image[y, start_x] == 255:
            if y == image.shape[0] - 1:
                return start_x, y
            elif (start_x, y + 1) in processed_points:
                return start_x, y
            continue
        elif image[y, start_x] == 0:
            return start_x, y - 1
        elif image[y, start_x] == 255 and y == image.shape[0] - 1:
            return start_x, y

    return None

def generate_contour_points(x, y, w, h):
    points = [(x, y)] # Top left corner
    points.extend([(x+i, y) for i in range(1, w)]) # Top edge
    points.extend([(x+w-1, y+j) for j in range(1, h)]) # Right edge
    points.extend([(x+w-1-i, y+h-1) for i in range(1, w)]) # Bottom edge
    points.extend([(x, y+h-1-j) for j in range(1, h)]) # Left edge
    return points

def find_starting_point(image: np.ndarray, processed_points: list[tuple[int, int]]):
    for x in range(image.shape[1]):
        for y in range(image.shape[0]):
            if (x, y) not in processed_points and image[y, x] == 255:
                return x, y
    return None, None

def calculate_rectangle_area(rectangle: tuple[int, int, int, int]):
    return rectangle[2] * rectangle[3]

def is_smaller_than_any_rectangle(rectangle, rectangles):
    rectangle_area = calculate_rectangle_area(rectangle)
    for r in rectangles:
        if calculate_rectangle_area(r) > rectangle_area:
            return True
    return False

def generate_line_points(start_x, start_y, end_x, end_y):
    points = []
    if start_x == end_x:
        for y in range(start_y, end_y + 1):
            points.append((start_x, y))
    elif start_y == end_y:
        for x in range(start_x, end_x + 1):
            points.append((x, start_y))
    return points

def calculate_line_length(start_point, end_point):
    return int(((start_point[0] - end_point[0]) ** 2 + (start_point[1] - end_point[1]) ** 2) ** 0.5) + 1

def find_top_line(image: np.ndarray, start_point: tuple[int, int], min_length=65):
    for x in range(start_point[0], image.shape[1]):
        for y in range(start_point[1], image.shape[0]):
            end_x, end_y = expand_right_from_point(image, (x, y), None)
            length = calculate_line_length(start_point, (end_x, end_y))
            if length >= min_length:
                return ((x, y), (end_x, end_y))

def find_left_line(image: np.ndarray, start_point: tuple[int, int], min_length=65):
    for y in range(start_point[1], image.shape[0]):
        for x in range(start_point[0], image.shape[1]):
            end_x, end_y = expand_down_from_point(image, (x, y), None)
            length = calculate_line_length(start_point, (end_x, end_y))
            if length >= min_length:
                return ((x, y), (end_x, end_y))
            
def find_bottom_line(image: np.ndarray, left_line_start, left_line_end, min_length=65):
    for current_y in range(left_line_end[1], left_line_start[1], -1):
        end_x, end_y = expand_right_from_point(image, (left_line_end[0], current_y), None)
        length = calculate_line_length((left_line_start[1], current_y), (end_x, end_y))
        if length >= min_length:
            return ((left_line_end[0], current_y), (end_x, end_y))

def find_right_line(top_line_start, top_line_end, bottom_line_start, bottom_line_end):
    top_line_length = calculate_line_length(top_line_start, top_line_end)
    bottom_line_length = calculate_line_length(bottom_line_start, bottom_line_end)
    if top_line_length == bottom_line_length:
        return ((top_line_end[0], top_line_end[1]), (bottom_line_end[0], bottom_line_end[1]))

def equalize_lines(top_line_start, top_line_end, bottom_line_start, bottom_line_end):
    top_line_length = calculate_line_length(top_line_start, top_line_end)
    bottom_line_length = calculate_line_length(bottom_line_start, bottom_line_end)
    if top_line_length > bottom_line_length:
        top_line_end = (bottom_line_end[0], top_line_end[1])
    elif bottom_line_length > top_line_length:
        bottom_line_end = (top_line_end[0], bottom_line_end[1])
    return (
        (top_line_start, top_line_end),
        (bottom_line_start, bottom_line_end)
    )


def main():

    # image_name = "rect_test.png"
    # image_name = "rect_test_10x10.png"
    # image_name = "rect_test_100x100.png"
    # image_name = "rect_test_500x500.png"
    # image_name = "rect_test_500x500_2.png"
    # image_name = "rect_uneven.png"
    # image_name = "rect_uneven_2.png"
    image_name = "rect_uneven_3.png"
    image = cv2.imread(image_name)
    image_color = image.copy()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = OCR.binarize_image(image, 127)

    # ToDo:
    # - Don't expand the left line downwards. Crop it out to same length as right line and check if all pixels are white.
    # - If left and right lines match, don't expand the bottom line. Just make it equal to top line length.
    # - When screenshoting tooltip do it around "Level" text.

    processed_points = set()
    starting_point = find_starting_point(image, processed_points)

    while starting_point not in processed_points and starting_point != (None, None):
        print(f"\nStarting point: {starting_point[0]}, {starting_point[1]}")

        min_line_length = 65
        top_line_start, top_line_end = find_top_line(image, starting_point, min_length=min_line_length)
        left_line_start, left_line_end = find_left_line(image, top_line_start, min_length=min_line_length)
        top_line_start = left_line_start # Crop off any excess from the top line
        bottom_line_start, bottom_line_end = find_bottom_line(image, left_line_start, left_line_end, min_length=min_line_length)
        left_line_end = bottom_line_start # Crop off any excess from the left line
        
        top_line_points, bottom_line_points = equalize_lines(top_line_start, top_line_end, bottom_line_start, bottom_line_end)
        top_line_start, top_line_end = top_line_points
        bottom_line_start, bottom_line_end = bottom_line_points
        
        right_line_start, right_line_end = find_right_line(top_line_start, top_line_end, bottom_line_start, bottom_line_end)

        image_color = cv2.line(image_color, (top_line_start[0], top_line_start[1]), (top_line_end[0], top_line_end[1]), (0, 255, 0), 1)
        image_color = cv2.line(image_color, (left_line_start[0], left_line_start[1]), (left_line_end[0], left_line_end[1]), (0, 255, 0), 1)
        image_color = cv2.line(image_color, (bottom_line_start[0], bottom_line_start[1]), (bottom_line_end[0], bottom_line_end[1]), (0, 255, 0), 1)
        image_color = cv2.line(image_color, (right_line_start[0], right_line_start[1]), (right_line_end[0], right_line_end[1]), (0, 255, 0), 1)
        img = cv2.resize(image_color, (500, 500))
        cv2.imshow("image", img)
        cv2.waitKey(0)
        return


if __name__ == "__main__":
    main()

from time import perf_counter, sleep

import cv2
import numpy as np

from src.utilities.image_detection import ImageDetection
from src.utilities.ocr.ocr import OCR
from src.utilities.screen_capture import ScreenCapture


def expand_right_from_point(image: np.ndarray, start_x, start_y, processed_points=None):
    if processed_points is None:
        processed_points = set()

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

def expand_down_from_point(image: np.ndarray, start_x, start_y, processed_points=None):
    if processed_points is None:
        processed_points = set()

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

def contains_point_with_x(points, x):
    for point in points:
        if point[0] == x:
            return True
    return False

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

def expand_down_across_line(image: np.ndarray, line_points, min_line_length, processed_points=None):
    for start_point in line_points[::-1]:
        end_point = expand_down_from_point(image, start_point[0], start_point[1], processed_points)
        if end_point is not None and calculate_line_length(start_point, end_point) > min_line_length:
            return start_point, end_point, generate_line_points(start_point[0], start_point[1], end_point[0], end_point[1])
    return None

def distance_between_points(point_1, point_2):
    return int(((point_1[0] - point_2[0]) ** 2 + (point_1[1] - point_2[1]) ** 2) ** 0.5)

def calculate_line_length(start_point, end_point):
    return distance_between_points(start_point, end_point) + 1


def main():

    # image_name = "rect_test.png"
    # image_name = "rect_test_10x10.png"
    image_name = "rect_test_100x100.png"
    # image_name = "rect_test_500x500.png"
    # image_name = "rect_test_500x500_2.png"
    # image_name = "rect_uneven.png"
    # image_name = "rect_uneven_2.png"
    image = cv2.imread(image_name)
    image_color = image.copy()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = OCR.binarize_image(image, 127)

    # ToDo:
    # - Don't expand the left line downwards. Crop it out to same length as right line and check if all pixels are white.
    # - If left and right lines match, don't expand the bottom line. Just make it equal to top line length.

    processed_points = set()
    starting_point = find_starting_point(image, processed_points)

    while starting_point not in processed_points and starting_point != (None, None):
        print(f"\nStarting point: {starting_point[0]}, {starting_point[1]}")

        top_line_start_x, top_line_start_y = starting_point
        top_line_end_x, top_line_end_y = expand_right_from_point(image, top_line_start_x, top_line_start_y, processed_points)
        top_line_points = generate_line_points(top_line_start_x, top_line_start_y, top_line_end_x, top_line_end_y)


        right_line_info = expand_down_across_line(image, top_line_points, min_line_length=5)
        if right_line_info is not None:
            right_line_start_x, right_line_start_y = right_line_info[0]
            right_line_end_x, right_line_end_y = right_line_info[1]
            top_line_end_x, top_line_end_y = right_line_start_x, right_line_start_y
            processed_points.update(right_line_info[2])
            processed_points.update(top_line_points)
        else:
            processed_points.update(top_line_points)
            # processed_points.update(right_line_info)
            continue
    
        left_line_start_x, left_line_start_y = top_line_start_x, top_line_start_y
        left_line_end_x, left_line_end_y = expand_down_from_point(
            image, 
            left_line_start_x, 
            left_line_start_y, 
            processed_points, # try to add points not including the top line start point
            # could add right line points here and check within the loop if
        )

        left_line_length = calculate_line_length(
            (left_line_start_x, left_line_start_y),
            (left_line_end_x, left_line_end_y)
        )
        right_line_length = calculate_line_length(
            (right_line_start_x, right_line_end_x),
            (right_line_start_y, right_line_end_y)
        )
        if left_line_length < right_line_length:
            processed_points.update(top_line_points)
            processed_points.update(generate_line_points(left_line_start_x, left_line_start_y, left_line_end_x, left_line_end_y))
            processed_points.add(starting_point)
            starting_point = find_starting_point(image, processed_points)
            continue

        bottom_line_start_x, bottom_line_start_y = left_line_end_x, left_line_end_y
        bottom_line_end_x, bottom_line_end_y = expand_right_from_point(image, bottom_line_start_x, bottom_line_start_y, processed_points)

        rectangle = (
            top_line_start_x, 
            top_line_start_y, 
            calculate_line_length((top_line_start_x, top_line_start_y), (top_line_end_x, top_line_end_y)),
            calculate_line_length((top_line_start_x, top_line_start_y), (left_line_end_x, left_line_end_y))
        )
        print(f"Found rectangle: {rectangle}")
        rectangle_contour_points = generate_contour_points(*rectangle)
        processed_points.update(rectangle_contour_points)
        processed_points.add(starting_point)
        starting_point = find_starting_point(image, processed_points)


        # image_color = cv2.line(image_color, (top_line_start_x, top_line_start_y), (top_line_end_x, top_line_end_y), (0, 255, 0), 1)
        # image_color = cv2.line(image_color, (right_line_start_x, right_line_start_y), (right_line_end_x, right_line_end_y), (0, 255, 0), 1)
        # image_color = cv2.line(image_color, (left_line_start_x, left_line_start_y), (left_line_end_x, left_line_end_y), (0, 255, 0), 1)
        # image_color = cv2.line(image_color, (bottom_line_start_x, bottom_line_start_y), (bottom_line_end_x, bottom_line_end_y), (0, 255, 0), 1)
        image_color = ImageDetection.draw_rectangle(image_color, rectangle, thickness=1)
        img = cv2.resize(image_color, (500, 500))
        cv2.imshow("image", img)
        cv2.waitKey(0)




        # left_line_x, left_line_y = expand_down_from_point(image, start_white_x, start_white_y, processed_points)
        # bottom_line_x, bottom_line_y = expand_right_from_point(image, left_line_x, left_line_y, processed_points)
        # print(f"\nTop line: {start_white_x}, {start_white_y} -> {top_line_end_x}, {top_line_end_y}")
        # print(f"Left line: {start_white_x}, {start_white_y} -> {left_line_x}, {left_line_y}")
        # print(f"Bottom line: {left_line_x}, {left_line_y} -> {bottom_line_x}, {bottom_line_y}")

        # top_line_length = calculate_line_length(start_white_x, top_line_end_x)
        # left_line_length = calculate_line_length(start_white_y, left_line_y)

        # if top_line_length > 20 or left_line_length > 20:

        #     bottom_line_length = calculate_line_length(left_line_x, bottom_line_x)
        #     print(f"Top line length: {top_line_length}")
        #     print(f"Left line length: {left_line_length}")
        #     print(f"Bottom line length: {bottom_line_length}")

        #     if top_line_length == bottom_line_length:
        #         right_line_x, right_line_y = expand_down_from_point(image, top_line_end_x, top_line_end_y, processed_points)
        #         print(f"Right line: {top_line_end_x}, {top_line_end_y} -> {right_line_x}, {right_line_y}")
        #         right_line_length = calculate_line_length(top_line_end_y, right_line_y)
        #         print(f"Right line length: {right_line_length}")

        #         if left_line_length == right_line_length:
        #             rectangle = (start_white_x, start_white_y, top_line_length, left_line_length)
        #             print(f"\nFound rectangle: {rectangle}")
        #             drawing_image = image_color.copy()
        #             drawing_image = ImageDetection.draw_rectangle(drawing_image, rectangle, thickness=1)
        #             drawing_image = cv2.resize(drawing_image, (500, 500))
        #             cv2.imshow("image", drawing_image)
        #             cv2.waitKey(0)
        #             processed_points.update(generate_contour_points(*rectangle))

        #         else:
        #             processed_points.add(starting_point)

        #     else:
        #         processed_points.add(starting_point)

        # else:
        #     processed_points.add(starting_point)

        # processed_points.add(starting_point)
        # starting_point = find_starting_point(image, processed_points)



if __name__ == "__main__":
    main()

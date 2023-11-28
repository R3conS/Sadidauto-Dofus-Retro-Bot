from functools import wraps
from time import perf_counter
import os

import cv2
import numpy as np
import pyautogui as pyag
import win32api

from src.detection import Detection
from src.window_capture import WindowCapture
from src.ocr.ocr import OCR


class VaultActions:

    image_folder_path = "src\\state\\out_of_combat\\sub_state\\banking\\images"
    empty_slot_image = cv2.imread(os.path.join(image_folder_path, "empty_slot.png"), cv2.IMREAD_UNCHANGED)
    tab_equipment_open_image = cv2.imread(os.path.join(image_folder_path, "tab_equipment_open.png"), cv2.IMREAD_UNCHANGED)
    tab_equipment_closed_image = cv2.imread(os.path.join(image_folder_path, "tab_equipment_closed.png"), cv2.IMREAD_UNCHANGED)
    tab_resources_open_image = cv2.imread(os.path.join(image_folder_path, "tab_resources_open.png"), cv2.IMREAD_UNCHANGED)
    tab_resources_closed_image = cv2.imread(os.path.join(image_folder_path, "tab_resources_closed.png"), cv2.IMREAD_UNCHANGED)
    tab_misc_open_image = cv2.imread(os.path.join(image_folder_path, "tab_misc_open.png"), cv2.IMREAD_UNCHANGED)
    tab_misc_closed_image = cv2.imread(os.path.join(image_folder_path, "tab_misc_closed.png"), cv2.IMREAD_UNCHANGED)
    inventory_slot_coords = { # Middle of each slot.
       "row_1" : [(712, 275), (753, 276), (791, 276), (832, 276), (873, 278)],
       "row_2" : [(712, 315), (753, 316), (791, 316), (832, 316), (873, 318)],
       "row_3" : [(712, 355), (753, 356), (791, 356), (832, 356), (873, 358)],
       "row_4" : [(712, 395), (753, 396), (791, 396), (832, 396), (873, 398)],
       "row_5" : [(712, 435), (753, 436), (791, 436), (832, 436), (873, 438)],
       "row_6" : [(712, 475), (753, 476), (791, 476), (832, 476), (873, 478)],
       "row_7" : [(712, 515), (753, 516), (791, 516), (832, 516), (873, 518)],
    }
    inventory_slot_area = (687, 252, 227, 291)
    inventory_tab_area = (684, 187, 234, 69)

    @classmethod
    def deposit_items(cls, amount_of_items):
        pyag.moveTo(687, 275) # To the left of the first slot.
        pyag.click() # Click to make sure window is focused.
        pyag.keyDown("ctrl")
        pyag.keyDown("shift")
        for coords in cls.get_deposit_coordinates(amount_of_items):
            pyag.moveTo(coords[0], coords[1], duration=0.2) # Doesn't select items if moving faster
        pyag.click(clicks=2, interval=0.1)
        pyag.keyUp("shift")
        pyag.keyUp("ctrl")

    @classmethod
    def get_deposit_coordinates(cls, occupied_slots_amount):
        slots_per_row = 5
        slots_processed = 0
        extracted_coords = []
        for coords_list in cls.inventory_slot_coords.values():
            slots_needed = occupied_slots_amount - slots_processed
            if slots_needed >= slots_per_row:
                extracted_coords.extend([coords_list[0], coords_list[-1]])
                slots_processed += slots_per_row
            elif slots_needed < slots_per_row and slots_needed > 0:
                extracted_coords.extend([coords_list[0], coords_list[slots_needed - 1]])
                slots_processed += slots_needed
            if slots_processed >= occupied_slots_amount:
                break
        return extracted_coords

    @classmethod
    def get_amount_of_occuppied_slots(cls):
        total_slots = 0
        for _, slot_coords in cls.inventory_slot_coords.items():
            for _ in slot_coords:
                total_slots += 1
        return total_slots - cls.get_amount_of_empty_slots()

    @classmethod
    def get_amount_of_empty_slots(cls):
        rectangles = Detection.find_image(
            haystack=cls.get_inventory_slot_area_screenshot(),
            needle=cls.empty_slot_image,
            confidence=0.65,
            method=cv2.TM_CCOEFF_NORMED,
            get_best_match_only=False,
        )
        return len(cv2.groupRectangles(rectangles, 1, 0.5)[0])

    @classmethod
    def get_inventory_slot_area_screenshot(cls):
        return WindowCapture.custom_area_capture(cls.inventory_slot_area)

    @classmethod
    def get_inventory_tab_area_screenshot(cls):
        return WindowCapture.custom_area_capture(cls.inventory_tab_area)

    @classmethod
    def is_equipment_tab_open(cls):
        return len(
            Detection.find_image(
                haystack=cls.get_inventory_tab_area_screenshot(),
                needle=cls.tab_equipment_open_image,
                confidence=0.95,
                method=cv2.TM_CCOEFF_NORMED,
            )
        ) > 0

    @classmethod
    def is_misc_tab_open(cls):
        return len(
            Detection.find_image(
                haystack=cls.get_inventory_tab_area_screenshot(),
                needle=cls.tab_misc_open_image,
                confidence=0.95,
                method=cv2.TM_CCOEFF_NORMED,
            )
        ) > 0

    @classmethod
    def is_resources_tab_open(cls):
        return len(
            Detection.find_image(
                haystack=cls.get_inventory_tab_area_screenshot(),
                needle=cls.tab_resources_open_image,
                confidence=0.95,
                method=cv2.TM_CCOEFF_NORMED,
            )
        ) > 0

    def __handle_tab_opening(decorated_method):
        """Decorator."""
        @wraps(decorated_method)
        def wrapper(cls, *args, **kwargs):
            tab_name = decorated_method.__name__.split("_")[1]
            is_open_method = getattr(VaultActions, f"is_{tab_name}_tab_open")
            if not is_open_method():
                tab_icon = Detection.find_image(
                    haystack=cls.get_inventory_tab_area_screenshot(),
                    needle=getattr(VaultActions, f"tab_{tab_name}_closed_image"),
                    confidence=0.95,
                    method=cv2.TM_CCOEFF_NORMED,
                )
                tab_x, tab_y = Detection.get_rectangle_center_point(tab_icon)
                tab_x, tab_y = cls.inventory_tab_area[0] + tab_x, cls.inventory_tab_area[1] + tab_y
                pyag.moveTo(tab_x, tab_y)
                pyag.click()
                start_time = perf_counter()
                while perf_counter() - start_time <= 5:
                    if is_open_method():
                        return True
                return False
            return True
        return wrapper

    @classmethod
    @__handle_tab_opening
    def open_equipment_tab(cls):
        pass
    
    @classmethod
    @__handle_tab_opening
    def open_misc_tab(cls):
        pass
    
    @classmethod
    @__handle_tab_opening
    def open_resources_tab(cls):
        pass


class PodsGetter:

        @staticmethod
        def screenshot_tooltip_area():
            return WindowCapture.custom_area_capture((688, 527, 160, 30))

        @staticmethod
        def get_tooltip_rectangle_from_image(tooltip_area: np.ndarray):
            tooltip_area = OCR.convert_to_grayscale(tooltip_area)
            tooltip_area = cv2.morphologyEx(tooltip_area, cv2.MORPH_CLOSE, np.ones((4, 4), np.uint8))
            tooltip_area = OCR.invert_image(tooltip_area)
            tooltip_area = OCR.binarize_image(tooltip_area, 180)
            canny = cv2.Canny(tooltip_area, 50, 150)
            contours, _ = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                epsilon = 0.05 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                x, y, w, h = cv2.boundingRect(approx)
                if w > 50 and h > 18:
                    return x, y, w, h
            return None

        @staticmethod
        def crop_tooltip_from_image(screenshot: np.ndarray, rectangle: tuple[int, int, int, int]):
            x, y, w, h = rectangle
            return screenshot[y:y+h, x:x+w]

        @staticmethod
        def read_text_from_tooltip(tooltip: np.ndarray):
            tooltip = OCR.convert_to_grayscale(tooltip)
            tooltip = OCR.invert_image(tooltip)
            tooltip = OCR.resize_image(tooltip, tooltip.shape[1] * 5, tooltip.shape[0] * 5)
            tooltip = OCR.dilate_image(tooltip, 2)
            tooltip = OCR.binarize_image(tooltip, 145)
            tooltip = cv2.GaussianBlur(tooltip, (3, 3), 0)
            return OCR.get_text_from_image(tooltip, ocr_engine="tesserocr")

        @staticmethod
        def trigger_pods_tooltip():
            pyag.moveTo(735, 560)

        @staticmethod
        def hide_pods_tooltip():
            pyag.moveTo(735, 580)

        @classmethod
        def is_pods_tooltip_visible(cls):
            tooltip_area = cls.screenshot_tooltip_area()
            tooltip_rectangle = cls.get_tooltip_rectangle_from_image(tooltip_area)
            if tooltip_rectangle is not None:
                return True
            return False

        @classmethod
        def get_pods_numbers(cls) -> tuple[int, int]:
            cls.trigger_pods_tooltip()
            start_time = perf_counter()
            while perf_counter() - start_time <= 5:
                if cls.is_pods_tooltip_visible():
                    tooltip_area = cls.screenshot_tooltip_area()
                    tooltip_rectangle = cls.get_tooltip_rectangle_from_image(tooltip_area)
                    cls.hide_pods_tooltip()
                    if tooltip_rectangle is not None:
                        tooltip = cls.crop_tooltip_from_image(tooltip_area, tooltip_rectangle)
                        text = cls.read_text_from_tooltip(tooltip)
                        return cls.parse_tooltip_text(text)
            raise Exception(f"Timed out while getting pods amount.")
        
        @staticmethod
        def parse_tooltip_text(extracted_tooltip_text) -> tuple[int, int]:
            split_text = extracted_tooltip_text.split("pods out of")
            numbers = []
            for text in split_text:
                text = text.strip()
                text = text.replace(" ", "")
                number = ""
                for char in text:
                    if char.isdigit():
                        number += char
                numbers.append(int(number))
            return tuple(numbers)

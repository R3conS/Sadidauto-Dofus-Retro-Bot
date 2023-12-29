from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from abc import ABC
import os
from time import perf_counter

import cv2
import pyautogui as pyag

from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture
from src.utilities import load_image_full_path
from src.bot._states.out_of_combat._status_enum import Status
from src.bot._states.out_of_combat._pods_reader.reader import PodsReader
from src.bot._exceptions import RecoverableException


class BaseTab(ABC):

    IMAGE_FOLDER_PATH = "src\\bot\\_states\\out_of_combat\\_sub_states\\banking\\_vault\\_tabs\\_images"
    INVENTORY_TAB_ICON_AREA = (684, 187, 234, 69)
    INVENTORY_SLOT_AREA = (687, 252, 227, 291)
    INVENTORY_SLOT_COORDS = { # Middle of each slot.
       "row_1" : [(712, 276), (752, 276), (792, 276), (832, 276), (872, 276)],
       "row_2" : [(712, 316), (752, 316), (792, 316), (832, 316), (872, 316)],
       "row_3" : [(712, 356), (752, 356), (792, 356), (832, 356), (872, 356)],
       "row_4" : [(712, 396), (752, 396), (792, 396), (832, 396), (872, 396)],
       "row_5" : [(712, 436), (752, 436), (792, 436), (832, 436), (872, 436)],
       "row_6" : [(712, 476), (752, 476), (792, 476), (832, 476), (872, 476)],
       "row_7" : [(712, 516), (752, 516), (792, 516), (832, 516), (872, 516)],
    }
    EMPTY_SLOT_IMAGE = load_image_full_path(os.path.join(IMAGE_FOLDER_PATH, "empty_slot.png"))

    def __init__(
            self, 
            name: str,
            tab_open_image_paths: list,
            tab_closed_image_paths: list,
            forbidden_item_image_paths: dict
        ):
        self._name = name.capitalize()
        self._tab_open_image_paths = tab_open_image_paths
        self._tab_open_images_loaded = self._load_tab_icon_images(tab_open_image_paths)
        self._tab_closed_image_paths = tab_closed_image_paths
        self._tab_closed_images_loaded = self._load_tab_icon_images(tab_closed_image_paths)
        self._forbidden_item_image_paths = forbidden_item_image_paths
        self._forbidden_item_images_loaded = self._load_forbidden_item_images(forbidden_item_image_paths)

    def is_tab_open(self):
        return len(
            ImageDetection.find_images(
                haystack=self._screenshot_inventory_tab_icon_area(),
                needles=self._tab_open_images_loaded,
                confidence=0.95,
                method=cv2.TM_SQDIFF_NORMED,
            )
        ) > 0

    def open_tab(self):
        log.info(f"Opening '{self._name}' tab ...")
        if self.is_tab_open():
            log.info(f"'{self._name}' tab is already open.")
            return
        pyag.moveTo(*self._get_icon_position())
        pyag.click()
        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if self.is_tab_open():
                log.info(f"Successfully opened '{self._name}' tab.")
                return
        raise RecoverableException(f"Timed out while trying to open '{self._name}' tab.")

    def deposit_tab(self):
        self.open_tab()
        if self._are_any_forbidden_items_loaded():
            log.info(f"'{self._name}' tab has forbidden items loaded. Depositing slot by slot ...")
            self._deposit_slot_by_slot()
        else:
            log.info(f"No forbidden items detected in '{self._name}' tab. Will deposit in bulk.")
            self._deposit_in_bulk()

    def _deposit_slot(self, slot_x, slot_y):
        pyag.keyDown("ctrl")
        pyag.moveTo(slot_x, slot_y)
        pyag.click(clicks=2, interval=0.1)
        pyag.keyUp("ctrl")

    def _deposit_visible_items(self, amount_of_items):
        pyag.moveTo(687, 275) # To the left of the first slot.
        pyag.click() # Click to make sure window is focused.
        pyag.keyDown("ctrl")
        pyag.keyDown("shift")
        for coords in self._get_coordinates_for_in_bulk_deposit(amount_of_items):
            pyag.moveTo(coords[0], coords[1], duration=0.2) # Doesn't select items if moving faster
        pyag.click(clicks=2, interval=0.1)
        pyag.keyUp("shift")
        pyag.keyUp("ctrl")

    def _deposit_slot_by_slot(self):
        # ToDo: remove None checks when PodsReader is refactored with exceptions.
        pods_before_deposit = PodsReader.BANK.get_occupied_pods()
        if pods_before_deposit is None:
            raise RecoverableException("Failed to get occupied bank pods.")
        
        slot_coords = self.INVENTORY_SLOT_COORDS["row_1"][0]
        deposited_items_count = 0
        while True:
            if self._is_slot_empty(*slot_coords):
                pods_after_deposit = PodsReader.BANK.get_occupied_pods()
                if pods_after_deposit is None:
                    raise RecoverableException("Failed to get occupied bank pods.")
                log.info(
                    f"Successfully deposited all items in the tab! "
                    f"Total items deposited: {deposited_items_count}. "
                    f"Pods freed: {pods_before_deposit - pods_after_deposit}."
                )
                return
            
            if not self._is_item_in_slot_forbidden(*slot_coords):
                self._deposit_slot(*slot_coords)
                if self._was_slot_deposited(*slot_coords):
                    deposited_items_count += 1
                    continue
                raise RecoverableException("Failed to deposit slot.")
            else:
                log.info(f"Skipping forbidden item '{self._get_forbidden_item_name(*slot_coords)}'.")
                slot_coords = self._get_next_slot_coords(*slot_coords)

    def _deposit_in_bulk(self):
        """
        Deposit all items in the tab by repeatedly selecting all items 
        while holding ctrl+shift and double clicking.
        """
        is_first_iteration = True
        while True:
            occupied_slots_amount = self._get_amount_of_occupied_inventory_slots()
            if occupied_slots_amount == 0:
                if is_first_iteration:
                    log.info("No items to deposit.")
                    return
                else:
                    log.info("Successfully deposited all items in the tab!")
                    return
            is_first_iteration = False

            # ToDo: remove None checks when PodsReader is refactored with exceptions.
            log.info(f"Depositing {occupied_slots_amount} items ...")
            pods_before_deposit = PodsReader.BANK.get_occupied_pods()
            if pods_before_deposit is None:
                raise RecoverableException("Failed to get occupied bank pods.")
            
            self._deposit_visible_items(occupied_slots_amount)

            pods_after_deposit = PodsReader.BANK.get_occupied_pods()
            if pods_after_deposit is None:
                log.error("Failed to get occupied bank pods.")
                raise RecoverableException("Failed to get occupied bank pods.")

            if pods_after_deposit < pods_before_deposit:
                log.info(
                    f"Successfully deposited {occupied_slots_amount} items! "
                    f"Pods freed: {pods_before_deposit - pods_after_deposit}."
                )
            else:
                raise RecoverableException("Failed to deposit items in bulk.")

    def _get_icon_position(self):
        if not self.is_tab_open():
            rectangles = ImageDetection.find_images(
                haystack=self._screenshot_inventory_tab_icon_area(),
                needles=self._tab_closed_images_loaded,
                confidence=0.95,
                method=cv2.TM_SQDIFF_NORMED,
            )
        else:
            rectangles = ImageDetection.find_images(
                haystack=self._screenshot_inventory_tab_icon_area(),
                needles=self._tab_open_images_loaded,
                confidence=0.95,
                method=cv2.TM_SQDIFF_NORMED,
            )
        if len(rectangles) > 0:
            center_point = ImageDetection.get_rectangle_center_point(rectangles[0])
            return (
                center_point[0] + self.INVENTORY_TAB_ICON_AREA[0],
                center_point[1] + self.INVENTORY_TAB_ICON_AREA[1]
            )
        raise RecoverableException(f"Failed to find '{self._name}' tab icon.")

    @staticmethod
    def _get_slot_rectangle(slot_center_x, slot_center_y):
        slot_width = 40
        slot_height = 40
        return (
            int(slot_center_x - (slot_width / 2)), 
            int(slot_center_y - (slot_height / 2)),
            slot_width,
            slot_height
        )

    def _get_amount_of_occupied_inventory_slots(self):
        total_slots = 0
        for _, slot_coords in self.INVENTORY_SLOT_COORDS.items():
            for _ in slot_coords:
                total_slots += 1
        return total_slots - self._get_amount_of_empty_slots()

    def _get_amount_of_empty_slots(self):
        rectangles = ImageDetection.find_image(
            haystack=self._screenshot_inventory_slot_area(),
            needle=self.EMPTY_SLOT_IMAGE,
            confidence=0.65,
            method=cv2.TM_CCOEFF_NORMED,
            get_best_match_only=False,
        )
        return len(cv2.groupRectangles(rectangles, 1, 0.5)[0])

    def _get_next_slot_coords(self, current_slot_x, current_slot_y):
        for row, slots in self.INVENTORY_SLOT_COORDS.items():
            for slot in slots:
                if slot[0] == current_slot_x and slot[1] == current_slot_y:
                    if slots.index(slot) == len(slots) - 1:
                        if row != "row_7":
                            next_row = list(self.INVENTORY_SLOT_COORDS.keys())[list(self.INVENTORY_SLOT_COORDS.keys()).index(row) + 1]
                            return self.INVENTORY_SLOT_COORDS[next_row][0]  # Return next row's first slot
                        else:
                            # ToDo: implement scrolling down.
                            return None  
                    else:
                        return self.INVENTORY_SLOT_COORDS[row][slots.index(slot) + 1]

    def _get_forbidden_item_name(self, slot_x, slot_y):
        for confidence, items in self._forbidden_item_images_loaded.items():
            for i, item in enumerate(items):
                rectangle = ImageDetection.find_image(
                    haystack=ScreenCapture.custom_area(self._get_slot_rectangle(slot_x, slot_y)),
                    needle=item,
                    confidence=confidence,
                    method=cv2.TM_CCORR_NORMED,
                    mask=ImageDetection.create_mask(item)
                )
                if len(rectangle) > 0:
                    name = os.path.splitext(os.path.basename(self._forbidden_item_image_paths[confidence][i]))[0]
                    return name.title()
        raise RecoverableException("Failed to get forbidden item name.")

    def _get_coordinates_for_in_bulk_deposit(self, occupied_slots_amount):
        slots_per_row = 5
        slots_processed = 0
        extracted_coords = []
        for coords_list in self.INVENTORY_SLOT_COORDS.values():
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

    def _is_slot_empty(self, slot_center_x, slot_center_y):
        rectangle = ImageDetection.find_image(
            haystack=ScreenCapture.custom_area(self._get_slot_rectangle(slot_center_x, slot_center_y)),
            needle=self.EMPTY_SLOT_IMAGE,
            confidence=0.99,
            method=cv2.TM_CCORR_NORMED,
        )
        if len(rectangle) > 0:
            return True
        return False

    def _is_item_in_slot_forbidden(self, slot_center_x, slot_center_y):
        """
        Best way to ensure consistent results is to prepare good images.
        Take a screenshot of the slot with the forbidden item by using 
        _screenshot_slot(), then make the upper half (20px) of the image 
        transparent. Also, different images might need different confidence 
        levels so make sure to test the item out once it's added.
        """
        for confidence, items in self._forbidden_item_images_loaded.items():
            for item in items:
                rectangle = ImageDetection.find_image(
                    haystack=ScreenCapture.custom_area(self._get_slot_rectangle(slot_center_x, slot_center_y)),
                    needle=item,
                    confidence=confidence,
                    method=cv2.TM_CCORR_NORMED,
                    mask=ImageDetection.create_mask(item)
                )
                if len(rectangle) > 0:
                    return True
        return False

    def _was_slot_deposited(self, slot_x, slot_y):
        next_slot_screenshot = self._screenshot_next_slot(slot_x, slot_y)
        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            current_slot_screenshot = self._screenshot_slot(slot_x, slot_y)
            rectangle = ImageDetection.find_image(
                haystack=current_slot_screenshot,
                needle=next_slot_screenshot,
                confidence=0.95,
                method=cv2.TM_CCORR_NORMED,
            )
            if len(rectangle) > 0:
                return True
        return False

    def _are_any_forbidden_items_loaded(self):
        return len(self._forbidden_item_images_loaded) > 0

    def _screenshot_slot(self, slot_center_x, slot_center_y):
        return ScreenCapture.custom_area(self._get_slot_rectangle(slot_center_x, slot_center_y))

    def _screenshot_next_slot(self, current_slot_center_x, current_slot_center_y):
        next_slot_coords = self._get_next_slot_coords(current_slot_center_x, current_slot_center_y)
        return ScreenCapture.custom_area(self._get_slot_rectangle(*next_slot_coords))

    def _screenshot_inventory_slot_area(self):
        return ScreenCapture.custom_area(self.INVENTORY_SLOT_AREA)

    def _screenshot_inventory_tab_icon_area(self):
        return ScreenCapture.custom_area(self.INVENTORY_TAB_ICON_AREA)

    @staticmethod
    def _load_tab_icon_images(image_paths: list):
        if not isinstance(image_paths, list):
            raise ValueError("'image_paths' argument must be of type 'list'.")
        if len(image_paths) == 0:
            raise ValueError("'image_paths' argument must contain at least one image path.")
        return [load_image_full_path(path) for path in image_paths]            

    @staticmethod
    def _load_forbidden_item_images(image_paths: dict):
        """Format: {image_detection_confidence: [image_path, ...]}"""
        if not isinstance(image_paths, dict):
            raise ValueError("Argument 'image_paths' must be of type 'dict'.")

        loaded_forbidden_items = {}
        for confidence, image_paths_list in image_paths.items():
            if not isinstance(confidence, float):
                raise ValueError("Argument's 'image_paths' keys (confidence) must be of type 'float'.")
            if confidence < 0 or confidence > 1:
                raise ValueError("Argument's 'image_paths' keys (confidence) must be between 0.0 and 1.0.")
            if not isinstance(image_paths_list, list):
                raise ValueError(f"Argument's 'image_paths' key values must be of type 'list'.")
            
            loaded_images = []
            for path in image_paths_list:
                loaded_images.append(load_image_full_path(path))
            loaded_forbidden_items[confidence] = loaded_images

        return loaded_forbidden_items

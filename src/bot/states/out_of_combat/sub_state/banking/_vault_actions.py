from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from functools import wraps
import os
from time import perf_counter

import cv2
import numpy as np
import pyautogui as pyag

from src.utilities import load_image
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture
from src.bot.states.out_of_combat.pods_reader.pods_reader import PodsReader
from src.bot.states.out_of_combat.status_enum import Status


def _handle_tab_opening(decorated_method):
    """Decorator."""
    @wraps(decorated_method)
    def wrapper(cls, *args, **kwargs):
        tab_name = decorated_method.__name__.split("_")[1]
        is_tab_open = getattr(VaultActions, f"is_{tab_name}_tab_open")
        
        if is_tab_open():
            log.info(f"'{tab_name.capitalize()}' tab is already open.")
            return True

        log.info(f"Opening '{tab_name.capitalize()}' tab ...")
        tab_icon = ImageDetection.find_images(
            haystack=cls.get_inventory_tab_area_screenshot(),
            needles=getattr(VaultActions, f"_TAB_{tab_name.upper()}_CLOSED_IMAGES"),
            confidence=0.95,
            method=cv2.TM_SQDIFF_NORMED,
        )
        if len(tab_icon) > 0:
            tab_x, tab_y = ImageDetection.get_rectangle_center_point(tab_icon[0])
            tab_x += cls._INVENTORY_TAB_AREA[0]
            tab_y += cls._INVENTORY_TAB_AREA[1]

            pyag.moveTo(tab_x, tab_y)
            pyag.click()

            start_time = perf_counter()
            while perf_counter() - start_time <= 5:
                if is_tab_open():
                    log.info(f"Successfully opened '{tab_name.capitalize()}' tab.")
                    return True
                
            log.error(f"Timed out while opening '{tab_name.capitalize()}' tab.")
            return False
        
        log.error(f"Failed to find '{tab_name.capitalize()}' tab icon.")
        return False
    
    return wrapper


def _handle_tab_depositing(decorated_method):
    """Decorator."""
    @wraps(decorated_method)
    def wrapper(cls, *args, **kwargs):
        tab_name = decorated_method.__name__.split("_")[1]
        getattr(VaultActions, f"open_{tab_name}_tab")()
        if not getattr(VaultActions, f"is_{tab_name}_tab_open")():
            log.error(f"Failed to open '{tab_name.capitalize()}' tab.")
            return Status.FAILED_TO_OPEN_TAB

        if getattr(VaultActions, f"does_{tab_name}_tab_have_forbidden_items_loaded")():
            log.info(f"'{tab_name.capitalize()}' tab has forbidden items loaded. Will deposit slot by slot.")
            return cls.deposit_tab_slot_by_slot(
                getattr(VaultActions, f"_FORBIDDEN_{tab_name.upper()}_ITEMS_LOADED"),
                getattr(VaultActions, f"_FORBIDDEN_{tab_name.upper()}_ITEMS")
            )
        else:
            log.info(f"No forbidden items detected for '{tab_name.capitalize()}' tab. Will mass deposit.")
            return cls.deposit_tab_mass()

    return wrapper


def _load_forbidden_items(
        folder_path: str, 
        forbidden_items: dict[float, list[str]]
    ) -> dict[float, list[np.ndarray]]:
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Path '{folder_path}' does not exist.")
    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"Folder '{folder_path}' does not exist.")
    
    loaded_forbidden_items = {}
    for confidence, item_names in forbidden_items.items():
        loaded_images = []
        for item_name in item_names:
            loaded_images.append(load_image(folder_path, item_name))
        loaded_forbidden_items[confidence] = loaded_images
    return loaded_forbidden_items


class VaultActions:

    _IMAGE_FOLDER_PATH = "src\\bot\\states\\out_of_combat\\sub_state\\banking\\images"
    _EMPTY_SLOT_IMAGE = load_image(_IMAGE_FOLDER_PATH, "empty_slot.png")
    _TAB_EQUIPMENT_OPEN_IMAGES = [
        load_image(_IMAGE_FOLDER_PATH, "tab_equipment_open.png"),
        load_image(_IMAGE_FOLDER_PATH, "tab_equipment_open_2.png")
    ]
    _TAB_EQUIPMENT_CLOSED_IMAGES = [
        load_image(_IMAGE_FOLDER_PATH, "tab_equipment_closed.png"),
        load_image(_IMAGE_FOLDER_PATH, "tab_equipment_closed_2.png")
    ]
    _TAB_RESOURCES_OPEN_IMAGES = [
        load_image(_IMAGE_FOLDER_PATH, "tab_resources_open.png"),
        load_image(_IMAGE_FOLDER_PATH, "tab_resources_open_2.png")
    ]
    _TAB_RESOURCES_CLOSED_IMAGES = [
        load_image(_IMAGE_FOLDER_PATH, "tab_resources_closed.png"),
        load_image(_IMAGE_FOLDER_PATH, "tab_resources_closed_2.png")
    ]
    _TAB_MISC_OPEN_IMAGES = [
        load_image(_IMAGE_FOLDER_PATH, "tab_misc_open.png"),
        load_image(_IMAGE_FOLDER_PATH, "tab_misc_open_2.png")
    ]
    _TAB_MISC_CLOSED_IMAGES = [
        load_image(_IMAGE_FOLDER_PATH, "tab_misc_closed.png"),
        load_image(_IMAGE_FOLDER_PATH, "tab_misc_closed_2.png")
    ]

    _INVENTORY_SLOT_COORDS = { # Middle of each slot.
       "row_1" : [(712, 276), (752, 276), (792, 276), (832, 276), (872, 276)],
       "row_2" : [(712, 316), (752, 316), (792, 316), (832, 316), (872, 316)],
       "row_3" : [(712, 356), (752, 356), (792, 356), (832, 356), (872, 356)],
       "row_4" : [(712, 396), (752, 396), (792, 396), (832, 396), (872, 396)],
       "row_5" : [(712, 436), (752, 436), (792, 436), (832, 436), (872, 436)],
       "row_6" : [(712, 476), (752, 476), (792, 476), (832, 476), (872, 476)],
       "row_7" : [(712, 516), (752, 516), (792, 516), (832, 516), (872, 516)],
    }
    _INVENTORY_SLOT_AREA = (687, 252, 227, 291)
    _INVENTORY_TAB_AREA = (684, 187, 234, 69)

    # Items that won't be deposited.
    _FORBIDDEN_EQUIPMENT_ITEMS_FOLDER_PATH = "src\\bot\\states\\out_of_combat\\sub_state\\banking\\images\\forbidden_equipment_items"
    _FORBIDDEN_EQUIPMENT_ITEMS = {}
    _FORBIDDEN_EQUIPMENT_ITEMS_LOADED = _load_forbidden_items(_FORBIDDEN_EQUIPMENT_ITEMS_FOLDER_PATH, _FORBIDDEN_EQUIPMENT_ITEMS)
    _FORBIDDEN_MISC_ITEMS_FOLDER_PATH = "src\\bot\\states\\out_of_combat\\sub_state\\banking\\images\\forbidden_misc_items"
    _FORBIDDEN_MISC_ITEMS = { # confidence: [image name, ...]
        0.99: ["recall_potion.png", "bonta_potion.png", "brakmar_potion.png"]
    }
    _FORBIDDEN_MISC_ITEMS_LOADED = _load_forbidden_items(_FORBIDDEN_MISC_ITEMS_FOLDER_PATH, _FORBIDDEN_MISC_ITEMS)
    _FORBIDDEN_RESOURCES_ITEMS_FOLDER_PATH = "src\\bot\\states\\out_of_combat\\sub_state\\banking\\images\\forbidden_resources_items"
    _FORBIDDEN_RESOURCES_ITEMS = {}
    _FORBIDDEN_RESOURCES_ITEMS_LOADED = _load_forbidden_items(_FORBIDDEN_RESOURCES_ITEMS_FOLDER_PATH, _FORBIDDEN_RESOURCES_ITEMS)

    @classmethod
    @_handle_tab_depositing
    def deposit_equipment_tab(cls):
        pass

    @classmethod
    @_handle_tab_depositing
    def deposit_misc_tab(cls):
        pass

    @classmethod
    @_handle_tab_depositing
    def deposit_resources_tab(cls):
        pass

    @classmethod
    def deposit_all_tabs(cls):
        deposit_methods = [
            cls.deposit_equipment_tab,
            cls.deposit_misc_tab,
            cls.deposit_resources_tab,
        ]
        for deposit_method in deposit_methods:
            status = deposit_method()
            if (
                status == Status.FAILED_TO_OPEN_TAB 
                or status == Status.FAILED_TO_DEPOSIT_ITEMS_IN_TAB
                or status == Status.FAILED_TO_DEPOSIT_SLOT
                or status == Status.FAILED_TO_GET_OCCUPIED_BANK_PODS
            ):
                return Status.FAILED_TO_DEPOSIT_ALL_TABS
        log.info("Successfully deposited all tabs.")
        return Status.SUCCESSFULLY_DEPOSITED_ALL_TABS

    @classmethod
    def deposit_tab_mass(cls):
        """
        Deposit all items in the tab by repeatedly selecting all items 
        while holding ctrl+shift and double clicking.
        """
        is_first_iteration = True
        while True:
            occupied_slots_amount = cls.get_amount_of_occupied_slots()
            if occupied_slots_amount == 0:
                if is_first_iteration:
                    log.info("No items to deposit.")
                    return Status.NO_ITEMS_TO_DEPOSIT_IN_TAB
                else:
                    log.info("Successfully deposited all items in the tab!")
                    return Status.SUCCESSFULLY_DEPOSITED_ITEMS_IN_TAB

            is_first_iteration = False

            log.info(f"Depositing {occupied_slots_amount} items ...")
            pods_before_deposit = PodsReader.get_occupied_bank_pods()
            if pods_before_deposit is None:
                log.error("Failed to get occupied bank pods.")
                return Status.FAILED_TO_GET_OCCUPIED_BANK_PODS
            cls.deposit_visible_items(occupied_slots_amount)
            pods_after_deposit = PodsReader.get_occupied_bank_pods()
            if pods_after_deposit is None:
                log.error("Failed to get occupied bank pods.")
                return Status.FAILED_TO_GET_OCCUPIED_BANK_PODS

            if pods_after_deposit < pods_before_deposit:
                log.info(
                    f"Successfully deposited {occupied_slots_amount} items! "
                    f"Pods freed: {pods_before_deposit - pods_after_deposit}."
                )
            else:
                log.error("Failed to deposit items.")
                return Status.FAILED_TO_DEPOSIT_ITEMS_IN_TAB

    @classmethod
    def deposit_tab_slot_by_slot(
        cls, 
        loaded_forbidden_items: dict[float, list[np.ndarray]],
        forbidden_items: dict[float, list[str]],
    ):
        pods_before_deposit = PodsReader.get_occupied_bank_pods()
        if pods_before_deposit is None:
            log.error("Failed to get occupied bank pods.")
            return Status.FAILED_TO_GET_OCCUPIED_BANK_PODS
        
        slot_coords = cls._INVENTORY_SLOT_COORDS["row_1"][0]
        deposited_items_count = 0
        while True:
            if cls.is_slot_empty(*slot_coords):
                pods_after_deposit = PodsReader.get_occupied_bank_pods()
                if pods_after_deposit is None:
                    log.error("Failed to get occupied bank pods.")
                    return Status.FAILED_TO_GET_OCCUPIED_BANK_PODS
                log.info(
                    f"Successfully deposited all items in the tab! "
                    f"Total items deposited: {deposited_items_count}. "
                    f"Pods freed: {pods_before_deposit - pods_after_deposit}."
                )
                return Status.SUCCESSFULLY_DEPOSITED_ITEMS_IN_TAB
            if not cls.is_item_forbidden(*slot_coords, loaded_forbidden_items):
                next_slot_screenshot = cls.screenshot_next_slot(*slot_coords)
                cls.deposit_slot(*slot_coords)
                if cls.was_slot_deposited(*slot_coords, next_slot_screenshot):
                    deposited_items_count += 1
                    continue
                log.error("Failed to deposit slot.")
                return Status.FAILED_TO_DEPOSIT_SLOT
            else:
                name = cls.get_forbidden_item_name(*slot_coords, loaded_forbidden_items, forbidden_items)
                log.info(f"Skipping forbidden item '{name}'.")
                slot_coords = cls.get_next_slot_coords(*slot_coords)

    @classmethod
    def deposit_visible_items(cls, amount_of_items):
        pyag.moveTo(687, 275) # To the left of the first slot.
        pyag.click() # Click to make sure window is focused.
        pyag.keyDown("ctrl")
        pyag.keyDown("shift")
        for coords in cls.get_deposit_coordinates(amount_of_items):
            pyag.moveTo(coords[0], coords[1], duration=0.2) # Doesn't select items if moving faster
        pyag.click(clicks=2, interval=0.1)
        pyag.keyUp("shift")
        pyag.keyUp("ctrl")

    @staticmethod
    def deposit_slot(slot_x, slot_y):
        pyag.keyDown("ctrl")
        pyag.moveTo(slot_x, slot_y)
        pyag.click(clicks=2, interval=0.1)
        pyag.keyUp("ctrl")

    @classmethod
    @_handle_tab_opening
    def open_equipment_tab(cls):
        pass
    
    @classmethod
    @_handle_tab_opening
    def open_misc_tab(cls):
        pass
    
    @classmethod
    @_handle_tab_opening
    def open_resources_tab(cls):
        pass

    @classmethod
    def is_equipment_tab_open(cls):
        return len(
            ImageDetection.find_images(
                haystack=cls.get_inventory_tab_area_screenshot(),
                needles=cls._TAB_EQUIPMENT_OPEN_IMAGES,
                confidence=0.95,
                method=cv2.TM_CCOEFF_NORMED,
            )
        ) > 0

    @classmethod
    def is_misc_tab_open(cls):
        return len(
            ImageDetection.find_images(
                haystack=cls.get_inventory_tab_area_screenshot(),
                needles=cls._TAB_MISC_OPEN_IMAGES,
                confidence=0.95,
                method=cv2.TM_CCOEFF_NORMED,
            )
        ) > 0

    @classmethod
    def is_resources_tab_open(cls):
        return len(
            ImageDetection.find_images(
                haystack=cls.get_inventory_tab_area_screenshot(),
                needles=cls._TAB_RESOURCES_OPEN_IMAGES,
                confidence=0.95,
                method=cv2.TM_CCOEFF_NORMED,
            )
        ) > 0

    @classmethod
    def is_item_forbidden(cls, slot_x, slot_y, forbidden_items_loaded: dict[float, list[np.ndarray]]):
        """
        Best way to ensure consistent results is to take a screenshot of the
        slot with the forbidden item by using screenshot_slot(),
        then make the upper half (20px) of the image transparent. Also, 
        different images might need different confidence levels so make
        sure to test the item out once it's added.
        """
        for confidence, items in forbidden_items_loaded.items():
            for item in items:
                rectangle = ImageDetection.find_image(
                    haystack=ScreenCapture.custom_area(cls.get_slot_rectangle(slot_x, slot_y)),
                    needle=item,
                    confidence=confidence,
                    method=cv2.TM_CCORR_NORMED,
                    mask=ImageDetection.create_mask(item)
                )
                if len(rectangle) > 0:
                    return True
        return False

    @classmethod
    def is_slot_empty(cls, slot_x, slot_y):
        rectangle = ImageDetection.find_image(
            haystack=ScreenCapture.custom_area(cls.get_slot_rectangle(slot_x, slot_y)),
            needle=VaultActions._EMPTY_SLOT_IMAGE,
            confidence=0.99,
            method=cv2.TM_CCORR_NORMED,
        )
        if len(rectangle) > 0:
            return True
        return False

    @classmethod
    def was_slot_deposited(cls, slot_x, slot_y, next_slot_screenshot):
        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            current_slot_screenshot = cls.screenshot_slot(slot_x, slot_y)
            rectangle = ImageDetection.find_image(
                haystack=current_slot_screenshot,
                needle=next_slot_screenshot,
                confidence=0.95,
                method=cv2.TM_CCORR_NORMED,
            )
            if len(rectangle) > 0:
                return True
        return False 

    @classmethod
    def does_equipment_tab_have_forbidden_items_loaded(cls):
        return len(cls._FORBIDDEN_EQUIPMENT_ITEMS_LOADED) > 0
    
    @classmethod
    def does_misc_tab_have_forbidden_items_loaded(cls):
        return len(cls._FORBIDDEN_MISC_ITEMS_LOADED) > 0
    
    @classmethod
    def does_resources_tab_have_forbidden_items_loaded(cls):
        return len(cls._FORBIDDEN_RESOURCES_ITEMS_LOADED) > 0

    @classmethod
    def get_deposit_coordinates(cls, occupied_slots_amount):
        slots_per_row = 5
        slots_processed = 0
        extracted_coords = []
        for coords_list in cls._INVENTORY_SLOT_COORDS.values():
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
    def get_amount_of_occupied_slots(cls):
        total_slots = 0
        for _, slot_coords in cls._INVENTORY_SLOT_COORDS.items():
            for _ in slot_coords:
                total_slots += 1
        return total_slots - cls.get_amount_of_empty_slots()

    @classmethod
    def get_amount_of_empty_slots(cls):
        rectangles = ImageDetection.find_image(
            haystack=cls.get_inventory_slot_area_screenshot(),
            needle=cls._EMPTY_SLOT_IMAGE,
            confidence=0.65,
            method=cv2.TM_CCOEFF_NORMED,
            get_best_match_only=False,
        )
        return len(cv2.groupRectangles(rectangles, 1, 0.5)[0])

    @classmethod
    def get_inventory_slot_area_screenshot(cls):
        return ScreenCapture.custom_area(cls._INVENTORY_SLOT_AREA)

    @classmethod
    def get_inventory_tab_area_screenshot(cls):
        return ScreenCapture.custom_area(cls._INVENTORY_TAB_AREA)

    @classmethod
    def get_forbidden_item_name(
        cls, 
        slot_x, 
        slot_y, 
        forbidden_items_loaded: dict[float, list[np.ndarray]],
        forbidden_items: dict[float, list[str]],
    ):
        for confidence, items in forbidden_items_loaded.items():
            for i, item in enumerate(items):
                rectangle = ImageDetection.find_image(
                    haystack=ScreenCapture.custom_area(cls.get_slot_rectangle(slot_x, slot_y)),
                    needle=item,
                    confidence=confidence,
                    method=cv2.TM_CCORR_NORMED,
                    mask=ImageDetection.create_mask(item)
                )
                if len(rectangle) > 0:
                    name = forbidden_items[confidence][i]
                    name = name.split(".")[0]
                    name = name.replace("_", " ")
                    return name.title()
        return None

    @classmethod
    def get_next_slot_coords(cls, current_slot_x, current_slot_y):
        for row, slots in cls._INVENTORY_SLOT_COORDS.items():
            for slot in slots:
                if slot[0] == current_slot_x and slot[1] == current_slot_y:
                    if slots.index(slot) == len(slots) - 1:
                        if row != "row_7":
                            next_row = list(cls._INVENTORY_SLOT_COORDS.keys())[list(cls._INVENTORY_SLOT_COORDS.keys()).index(row) + 1]
                            return cls._INVENTORY_SLOT_COORDS[next_row][0]  # Return next row's first slot
                        else:
                            # ToDo: implement scrolling down.
                            return None  
                    else:
                        return cls._INVENTORY_SLOT_COORDS[row][slots.index(slot) + 1]

    @classmethod
    def get_slot_rectangle(cls, slot_center_x, slot_center_y):
        slot_width = 40
        slot_height = 40
        return (
            int(slot_center_x - (slot_width / 2)), 
            int(slot_center_y - (slot_height / 2)),
            slot_width,
            slot_height
        )

    @classmethod
    def screenshot_next_slot(cls, current_slot_center_x, current_slot_center_y):
        next_slot_coords = cls.get_next_slot_coords(current_slot_center_x, current_slot_center_y)
        return ScreenCapture.custom_area(cls.get_slot_rectangle(*next_slot_coords))

    @classmethod
    def screenshot_slot(cls, slot_center_x, slot_center_y):
        return ScreenCapture.custom_area(cls.get_slot_rectangle(slot_center_x, slot_center_y))

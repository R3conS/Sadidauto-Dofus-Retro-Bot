from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from functools import wraps
from time import perf_counter
import os

import cv2
import pyautogui as pyag

from ._pods_getter import PodsGetter
from src.detection import Detection
from src.window_capture import WindowCapture


def _handle_tab_opening(decorated_method):
    """Decorator."""
    @wraps(decorated_method)
    def wrapper(cls, *args, **kwargs):
        tab_name = decorated_method.__name__.split("_")[1]
        is_tab_open = getattr(VaultActions, f"is_{tab_name}_tab_open")
        
        if is_tab_open():
            log.info(f"'{tab_name.capitalize()}' tab is open.")
            return f"{tab_name}_tab_is_already_open"

        tab_icon = Detection.find_image(
            haystack=cls.get_inventory_tab_area_screenshot(),
            needle=getattr(VaultActions, f"tab_{tab_name}_closed_image"),
            confidence=0.95,
            method=cv2.TM_CCOEFF_NORMED,
        )
        if len(tab_icon) > 0:
            tab_x, tab_y = Detection.get_rectangle_center_point(tab_icon)
            tab_x += cls.inventory_tab_area[0]
            tab_y += cls.inventory_tab_area[1]

            log.info(f"Opening '{tab_name.capitalize()}' tab ...")
            pyag.moveTo(tab_x, tab_y)
            pyag.click()

            start_time = perf_counter()
            while perf_counter() - start_time <= 5:
                if is_tab_open():
                    log.info(f"Successfully opened '{tab_name.capitalize()}' tab.")
                    return f"successfully_opened_{tab_name}_tab"
                
            log.info(f"Failed to open '{tab_name.capitalize()}' tab.")
            return f"failed_to_open_{tab_name}_tab"
        
        log.info(f"Failed to find '{tab_name.capitalize()}' tab icon.")
        return f"failed_to_find_{tab_name}_tab_icon"
    
    return wrapper


def _handle_tab_depositing(decorated_method):
    """Decorator."""
    @wraps(decorated_method)
    def wrapper(cls, *args, **kwargs):
        tab_name = decorated_method.__name__.split("_")[1]
        open_tab = getattr(VaultActions, f"open_{tab_name}_tab")
        is_tab_open = getattr(VaultActions, f"is_{tab_name}_tab_open")
        open_tab()
        if not is_tab_open():
            log.info(f"Failed to open '{tab_name.capitalize()}' tab.")
            return f"failed_to_open_{tab_name}_tab"

        is_first_iteration = True
        while True:
            occupied_slots_amount = cls.get_amount_of_occupied_slots()
            if occupied_slots_amount == 0:
                if is_first_iteration:
                    log.info(f"No items to deposit in '{tab_name.capitalize()}' tab.")
                    return f"no_items_to_deposit_in_{tab_name}_tab"
                else:
                    log.info(f"Finished depositing items in '{tab_name.capitalize()}' tab.")
                    return f"finished_depositing_items_in_{tab_name}_tab"

            is_first_iteration = False
            log.info(f"Depositing {occupied_slots_amount} items ...")
            pods_before_deposit = PodsGetter.get_pods_numbers()[0]
            cls.deposit_visible_items(occupied_slots_amount)
            pods_after_deposit = PodsGetter.get_pods_numbers()[0]

            if pods_after_deposit < pods_before_deposit:
                log.info(f"Successfully deposited {occupied_slots_amount} items! Pods freed: {pods_before_deposit - pods_after_deposit}.")
            else:
                log.info(f"Failed to deposit items in {tab_name.capitalize()} tab.")
                return f"failed_to_deposit_items_in_{tab_name}_tab"

    return wrapper


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
    def get_amount_of_occupied_slots(cls):
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

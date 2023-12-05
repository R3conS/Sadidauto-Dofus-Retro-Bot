from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from functools import wraps
from time import perf_counter

import cv2
import pyautogui as pyag

from src.utilities import load_image
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture
from .status_enum import Status


AVAILABLE_SPELLS = ["earthquake", "poisoned_wind", "sylvan_power", "bramble"]


def __get_spell_name(decorated_method_name):
    """Utility function for decorators."""
    for name in AVAILABLE_SPELLS:
        if name in decorated_method_name:
            return name
    raise ValueError(f"Failed to find allowed spell name in method name: {decorated_method_name}.")


def _is_spell_available(decorated_method):
    @wraps(decorated_method)
    def wrapper(cls, *args, **kwargs):
        return len(
            ImageDetection.find_image(
                haystack=ScreenCapture.custom_area(cls.spell_bar_area),
                needle=getattr(cls, f"{__get_spell_name(decorated_method.__name__)}_image"),
                confidence=0.99,
                method=cv2.TM_SQDIFF_NORMED,
            )
        ) > 0
    return wrapper


def _get_spell_icon_pos(decorated_method):
    @wraps(decorated_method)
    def wrapper(cls, *args, **kwargs):
        spell_name = __get_spell_name(decorated_method.__name__)
        images_and_masks = [
            (getattr(cls, f"{spell_name}_image"), None),
            (getattr(cls, f"{spell_name}_on_cooldown_image"), getattr(cls, f"{spell_name}_on_cooldown_image_mask"))
        ]
        for image, mask in images_and_masks:
            rectangle = ImageDetection.find_image(
                haystack=ScreenCapture.custom_area(cls.spell_bar_area),
                needle=image,
                confidence=0.98,
                method=cv2.TM_CCORR_NORMED if mask is not None else cv2.TM_SQDIFF_NORMED,
                mask=mask if mask is not None else None
            )
            if len(rectangle) > 0:
                # Returning the top left corner instead of the center in case
                # this method is used with one of the is_spell_selected() methods.
                # If the spell is on the second row of the spell bar and
                # the center is returned, the is_spell_selected() detection
                # will always return False because the images will be only
                # partially visible due to them being cut off by the bottom
                # of the game window.
                return rectangle[0] + cls.spell_bar_area[0], rectangle[1] + cls.spell_bar_area[1]
        return None
    return wrapper


def _is_spell_selected(decorated_method):
    @wraps(decorated_method)
    def wrapper(cls, *args, **kwargs):
        spell_name = __get_spell_name(decorated_method.__name__)
        screenshot = ScreenCapture.around_pos(pyag.position(), 75)
        images_and_masks = [
            (getattr(cls, f"{spell_name}_selected_cannot_cast_image"), getattr(cls, f"{spell_name}_selected_cannot_cast_image_mask")),
            (getattr(cls, f"{spell_name}_selected_can_cast_image"), None)
        ]
        for image, mask in images_and_masks:
            if len(
                ImageDetection.find_image(
                    haystack=screenshot,
                    needle=image,
                    confidence=0.98,
                    method=cv2.TM_CCORR_NORMED if mask is not None else cv2.TM_SQDIFF_NORMED,
                    mask=mask if mask is not None else None
                )
            ) > 0:
                return True
        return False
    return wrapper


def _is_spell_castable_on_pos(decorated_method):
    @wraps(decorated_method)
    def wrapper(cls, *args, **kwargs):
        spell_name = __get_spell_name(decorated_method.__name__)
        pyag.moveTo(*args)
        screenshot = ScreenCapture.around_pos(pyag.position(), 75)
        return len(
            ImageDetection.find_image(
                haystack=screenshot,
                needle=getattr(cls, f"{spell_name}_selected_can_cast_image"),
                confidence=0.97,
                method=cv2.TM_SQDIFF_NORMED
            )
        ) > 0
    return wrapper


def _select_spell(decorated_method):
    @wraps(decorated_method)
    def wrapper(cls, *args, **kwargs):
        # Making sure to deselect any other spells just in case. Otherwise
        # the can/cannot cast image might block one of the spell icon 
        # images and the get_spell_icon_pos() might return None causing this
        # whole method to fail.
        pyag.moveTo(929, 752)
        pyag.click()

        spell_name = __get_spell_name(decorated_method.__name__)
        spell_icon_pos = getattr(cls, f"get_{spell_name}_icon_pos")()
        if spell_icon_pos is None:
            return Status.FAILED_TO_GET_SPELL_ICON_POS
        
        pyag.moveTo(*spell_icon_pos)
        pyag.click()

        # Checking within a timer to give the game time to draw the
        # can cast/cannot cast image once spell pos is clicked.
        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if getattr(cls, f"is_{spell_name}_selected")():
                return Status.SUCCESSFULLY_SELECTED_SPELL
        return Status.FAILED_TO_SELECT_SPELL
    
    return wrapper


def _cast_spell(decorated_method):
    @wraps(decorated_method)
    def wrapper(cls, *args, **kwargs):
        spell_name = __get_spell_name(decorated_method.__name__)
        spell_name_formatted = spell_name.replace("_", " ").title()
        log.info(f"Attempting to cast: '{spell_name_formatted}' ... ")

        log.info(f"Selecting the spell ... ")
        result = getattr(cls, f"select_{spell_name}")()
        if (
            result == Status.FAILED_TO_GET_SPELL_ICON_POS
            or result == Status.FAILED_TO_SELECT_SPELL
        ):
            log.info(f"Failed to cast: '{spell_name_formatted}'. Reason: {result.value.replace('_', ' ')}.")
            return Status.FAILED_TO_CAST_SPELL
        log.info(f"Successfully selected.")
        
        log.info(f"Checking if spell is castable on position: {args[0], args[1]} ... ")
        pyag.moveTo(*args)
        if not getattr(cls, f"is_{spell_name}_castable_on_pos")(*args):
            log.info(f"Spell is not castable.")
            return Status.SPELL_IS_NOT_CASTABLE_ON_PROVIDED_POS
        log.info(f"Spell is castable.")

        log.info(f"Casting ... ")
        ap_area_before_casting = ScreenCapture.custom_area(cls.ap_area)
        pyag.click()
        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            ap_area_after_casting = ScreenCapture.custom_area(cls.ap_area)
            rectangle = ImageDetection.find_image(
                haystack=ap_area_after_casting,
                needle=ap_area_before_casting,
                confidence=0.98,
                method=cv2.TM_CCOEFF_NORMED,
            )
            if len(rectangle) <= 0: # If images are different then spell animation has finished.
                log.info(f"Successfully cast: '{spell_name_formatted}'.")
                pyag.moveTo(929, 752) # Move mouse off game area.
                return Status.SUCCESSFULLY_CAST_SPELL
        log.info(f"Timed out while detecting if '{spell_name_formatted}' was cast successfully.")
        return Status.TIMED_OUT_WHILE_DETECTING_IF_SPELL_CAST_SUCCESSFULLY
    
    return wrapper


class Spells:

    ap_area = (456, 611, 29, 25)
    spell_bar_area = (643, 658, 291, 99)
    image_folder_path = "src\\bot\\states\\in_combat\\sub_state\\fighting\\images\\spells"
    # Earthquake
    earthquake_image = load_image(image_folder_path, "earthquake.png")
    earthquake_selected_can_cast_image = load_image(image_folder_path, "earthquake_selected_can_cast.png")
    earthquake_selected_cannot_cast_image = load_image(image_folder_path, "earthquake_selected_cannot_cast.png")
    earthquake_selected_cannot_cast_image_mask = ImageDetection.create_mask(earthquake_selected_cannot_cast_image)
    earthquake_on_cooldown_image = load_image(image_folder_path, "earthquake_on_cooldown.png")
    earthquake_on_cooldown_image_mask = ImageDetection.create_mask(earthquake_on_cooldown_image)
    # Poisoned Wind
    poisoned_wind_image = load_image(image_folder_path, "poisoned_wind.png")
    poisoned_wind_selected_can_cast_image = load_image(image_folder_path, "poisoned_wind_selected_can_cast.png")
    poisoned_wind_selected_cannot_cast_image = load_image(image_folder_path, "poisoned_wind_selected_cannot_cast.png")
    poisoned_wind_selected_cannot_cast_image_mask = ImageDetection.create_mask(poisoned_wind_selected_cannot_cast_image)
    poisoned_wind_on_cooldown_image = load_image(image_folder_path, "poisoned_wind_on_cooldown.png")
    poisoned_wind_on_cooldown_image_mask = ImageDetection.create_mask(poisoned_wind_on_cooldown_image)
    # Sylvan Power
    sylvan_power_image = load_image(image_folder_path, "sylvan_power.png")
    sylvan_power_selected_can_cast_image = load_image(image_folder_path, "sylvan_power_selected_can_cast.png")
    sylvan_power_selected_cannot_cast_image = load_image(image_folder_path, "sylvan_power_selected_cannot_cast.png")
    sylvan_power_selected_cannot_cast_image_mask = ImageDetection.create_mask(sylvan_power_selected_cannot_cast_image)
    sylvan_power_on_cooldown_image = load_image(image_folder_path, "sylvan_power_on_cooldown.png")
    sylvan_power_on_cooldown_image_mask = ImageDetection.create_mask(sylvan_power_on_cooldown_image)
    # Bramble
    bramble_image = load_image(image_folder_path, "bramble.png")
    bramble_selected_can_cast_image = load_image(image_folder_path, "bramble_selected_can_cast.png")
    bramble_selected_cannot_cast_image = load_image(image_folder_path, "bramble_selected_cannot_cast.png")
    bramble_selected_cannot_cast_image_mask = ImageDetection.create_mask(bramble_selected_cannot_cast_image)
    bramble_on_cooldown_image = load_image(image_folder_path, "bramble_on_cooldown.png")
    bramble_on_cooldown_image_mask = ImageDetection.create_mask(bramble_on_cooldown_image)

    @classmethod
    @_is_spell_available
    def is_earthquake_available(cls):
        pass
    
    @classmethod
    @_is_spell_available
    def is_poisoned_wind_available(cls):
        pass
    
    @classmethod
    @_is_spell_available
    def is_sylvan_power_available(cls):
        pass

    @classmethod
    @_is_spell_available
    def is_bramble_available(cls):
        pass

    @classmethod
    @_get_spell_icon_pos
    def get_earthquake_icon_pos(cls):
        pass

    @classmethod
    @_get_spell_icon_pos
    def get_poisoned_wind_icon_pos(cls):
        pass

    @classmethod
    @_get_spell_icon_pos
    def get_sylvan_power_icon_pos(cls):
        pass

    @classmethod
    @_get_spell_icon_pos
    def get_bramble_icon_pos(cls):
        pass

    @classmethod
    @_is_spell_selected
    def is_earthquake_selected(cls):
        pass

    @classmethod
    @_is_spell_selected
    def is_poisoned_wind_selected(cls):
        pass

    @classmethod
    @_is_spell_selected
    def is_sylvan_power_selected(cls):
        pass

    @classmethod
    @_is_spell_selected
    def is_bramble_selected(cls):
        pass

    @classmethod
    @_is_spell_castable_on_pos
    def is_earthquake_castable_on_pos(cls, x, y):
        """For accurate results make sure the spell is selected."""
        pass

    @classmethod
    @_is_spell_castable_on_pos
    def is_poisoned_wind_castable_on_pos(cls, x, y):
        """For accurate results make sure the spell is selected."""
        pass

    @classmethod
    @_is_spell_castable_on_pos
    def is_sylvan_power_castable_on_pos(cls, x, y):
        """For accurate results make sure the spell is selected."""
        pass

    @classmethod
    @_is_spell_castable_on_pos
    def is_bramble_castable_on_pos(cls, x, y):
        """For accurate results make sure the spell is selected."""
        pass

    @classmethod
    @_select_spell
    def select_earthquake(cls):
        pass

    @classmethod
    @_select_spell
    def select_poisoned_wind(cls):
        pass

    @classmethod
    @_select_spell
    def select_sylvan_power(cls):
        pass

    @classmethod
    @_select_spell
    def select_bramble(cls):
        pass

    @classmethod
    @_cast_spell
    def cast_earthquake(cls, x, y):
        pass

    @classmethod
    @_cast_spell
    def cast_poisoned_wind(cls, x, y):
        pass

    @classmethod
    @_cast_spell
    def cast_sylvan_power(cls, x, y):
        pass

    @classmethod
    @_cast_spell
    def cast_bramble(cls, x, y):
        pass

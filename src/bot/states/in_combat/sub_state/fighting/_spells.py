from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from functools import wraps
from time import perf_counter

import cv2
import pyautogui as pyag

from src.utilities import load_image, move_mouse_off_game_area
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture
from .status_enum import Status


AVAILABLE_SPELLS = ["EARTHQUAKE", "POISONED_WIND", "SYLVAN_POWER", "BRAMBLE"]


def _get_spell_name(decorated_method_name: str):
    """Utility function for decorators."""
    decorated_method_name = decorated_method_name.upper()
    for name in AVAILABLE_SPELLS:
        if name in decorated_method_name:
            return name
    raise ValueError(f"Failed to find allowed spell name in method name: {decorated_method_name}.")


def _is_spell_available(decorated_method):
    @wraps(decorated_method)
    def wrapper(cls, *args, **kwargs):
        return len(
            ImageDetection.find_image(
                haystack=ScreenCapture.custom_area(cls._SPELL_BAR_AREA),
                needle=getattr(cls, f"_{_get_spell_name(decorated_method.__name__)}_IMAGE"),
                confidence=0.99,
                method=cv2.TM_SQDIFF_NORMED,
            )
        ) > 0
    return wrapper


def _get_spell_icon_pos(decorated_method):
    @wraps(decorated_method)
    def wrapper(cls, *args, **kwargs):
        spell_name = _get_spell_name(decorated_method.__name__)
        images_and_masks = [
            (getattr(cls, f"_{spell_name}_IMAGE"), None),
            (getattr(cls, f"_{spell_name}_ON_COOLDOWN_IMAGE"), getattr(cls, f"_{spell_name}_ON_COOLDOWN_IMAGE_MASK"))
        ]
        for image, mask in images_and_masks:
            rectangle = ImageDetection.find_image(
                haystack=ScreenCapture.custom_area(cls._SPELL_BAR_AREA),
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
                return rectangle[0] + cls._SPELL_BAR_AREA[0], rectangle[1] + cls._SPELL_BAR_AREA[1]
        return None
    return wrapper


def _is_spell_selected(decorated_method):
    @wraps(decorated_method)
    def wrapper(cls, *args, **kwargs):
        spell_name = _get_spell_name(decorated_method.__name__)
        screenshot = ScreenCapture.around_pos(pyag.position(), 75)
        images_and_masks = [
            (getattr(cls, f"_{spell_name}_SELECTED_CANNOT_CAST_IMAGE"), getattr(cls, f"_{spell_name}_SELECTED_CANNOT_CAST_IMAGE_MASK")),
            (getattr(cls, f"_{spell_name}_SELECTED_CAN_CAST_IMAGE"), None)
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
        spell_name = _get_spell_name(decorated_method.__name__)
        pyag.moveTo(*args)
        screenshot = ScreenCapture.around_pos(pyag.position(), 75)
        return len(
            ImageDetection.find_image(
                haystack=screenshot,
                needle=getattr(cls, f"_{spell_name}_SELECTED_CAN_CAST_IMAGE"),
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

        spell_name = _get_spell_name(decorated_method.__name__).lower()
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
        spell_name = _get_spell_name(decorated_method.__name__).lower()
        spell_name_formatted = spell_name.replace("_", " ").title()
        log.info(f"Attempting to cast: '{spell_name_formatted}' ... ")

        log.info(f"Selecting the spell ... ")
        result = getattr(cls, f"select_{spell_name}")()
        if (
            result == Status.FAILED_TO_GET_SPELL_ICON_POS
            or result == Status.FAILED_TO_SELECT_SPELL
        ):
            log.error(f"Failed to cast: '{spell_name_formatted}'. Reason: {result.value.replace('_', ' ')}.")
            return Status.FAILED_TO_CAST_SPELL
        log.info(f"Successfully selected.")
        
        log.info(f"Checking if spell is castable on position: {args[0], args[1]} ... ")
        pyag.moveTo(*args)
        if not getattr(cls, f"is_{spell_name}_castable_on_pos")(*args):
            log.info(f"Spell is not castable.")
            return Status.SPELL_IS_NOT_CASTABLE_ON_PROVIDED_POS
        log.info(f"Spell is castable.")

        log.info(f"Casting ... ")
        _AP_AREA_before_casting = ScreenCapture.custom_area(cls._AP_AREA)
        pyag.click()
        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            _AP_AREA_after_casting = ScreenCapture.custom_area(cls._AP_AREA)
            rectangle = ImageDetection.find_image(
                haystack=_AP_AREA_after_casting,
                needle=_AP_AREA_before_casting,
                confidence=0.98,
                method=cv2.TM_CCOEFF_NORMED,
            )
            if len(rectangle) <= 0: # If images are different then spell animation has finished.
                log.info(f"Successfully cast: '{spell_name_formatted}'.")
                move_mouse_off_game_area() # To make sure the vision of spell bar is not blocked.
                return Status.SUCCESSFULLY_CAST_SPELL
        log.error(f"Timed out while detecting if '{spell_name_formatted}' was cast successfully.")
        return Status.TIMED_OUT_WHILE_DETECTING_IF_SPELL_CAST_SUCCESSFULLY
    
    return wrapper


class Spells:

    _AP_AREA = (456, 611, 29, 25)
    _SPELL_BAR_AREA = (643, 658, 291, 99)
    _IMAGE_FOLDER_PATH = "src\\bot\\states\\in_combat\\sub_state\\fighting\\images\\spells"
    # Earthquake
    _EARTHQUAKE_IMAGE = load_image(_IMAGE_FOLDER_PATH, "earthquake.png")
    _EARTHQUAKE_SELECTED_CAN_CAST_IMAGE = load_image(_IMAGE_FOLDER_PATH, "earthquake_selected_can_cast.png")
    _EARTHQUAKE_SELECTED_CANNOT_CAST_IMAGE = load_image(_IMAGE_FOLDER_PATH, "earthquake_selected_cannot_cast.png")
    _EARTHQUAKE_SELECTED_CANNOT_CAST_IMAGE_MASK = ImageDetection.create_mask(_EARTHQUAKE_SELECTED_CANNOT_CAST_IMAGE)
    _EARTHQUAKE_ON_COOLDOWN_IMAGE = load_image(_IMAGE_FOLDER_PATH, "earthquake_on_cooldown.png")
    _EARTHQUAKE_ON_COOLDOWN_IMAGE_MASK = ImageDetection.create_mask(_EARTHQUAKE_ON_COOLDOWN_IMAGE)
    # Poisoned Wind
    _POISONED_WIND_IMAGE = load_image(_IMAGE_FOLDER_PATH, "poisoned_wind.png")
    _POISONED_WIND_SELECTED_CAN_CAST_IMAGE = load_image(_IMAGE_FOLDER_PATH, "poisoned_wind_selected_can_cast.png")
    _POISONED_WIND_SELECTED_CANNOT_CAST_IMAGE = load_image(_IMAGE_FOLDER_PATH, "poisoned_wind_selected_cannot_cast.png")
    _POISONED_WIND_SELECTED_CANNOT_CAST_IMAGE_MASK = ImageDetection.create_mask(_POISONED_WIND_SELECTED_CANNOT_CAST_IMAGE)
    _POISONED_WIND_ON_COOLDOWN_IMAGE = load_image(_IMAGE_FOLDER_PATH, "poisoned_wind_on_cooldown.png")
    _POISONED_WIND_ON_COOLDOWN_IMAGE_MASK = ImageDetection.create_mask(_POISONED_WIND_ON_COOLDOWN_IMAGE)
    # Sylvan Power
    _SYLVAN_POWER_IMAGE = load_image(_IMAGE_FOLDER_PATH, "sylvan_power.png")
    _SYLVAN_POWER_SELECTED_CAN_CAST_IMAGE = load_image(_IMAGE_FOLDER_PATH, "sylvan_power_selected_can_cast.png")
    _SYLVAN_POWER_SELECTED_CANNOT_CAST_IMAGE = load_image(_IMAGE_FOLDER_PATH, "sylvan_power_selected_cannot_cast.png")
    _SYLVAN_POWER_SELECTED_CANNOT_CAST_IMAGE_MASK = ImageDetection.create_mask(_SYLVAN_POWER_SELECTED_CANNOT_CAST_IMAGE)
    _SYLVAN_POWER_ON_COOLDOWN_IMAGE = load_image(_IMAGE_FOLDER_PATH, "sylvan_power_on_cooldown.png")
    _SYLVAN_POWER_ON_COOLDOWN_IMAGE_MASK = ImageDetection.create_mask(_SYLVAN_POWER_ON_COOLDOWN_IMAGE)
    # Bramble
    _BRAMBLE_IMAGE = load_image(_IMAGE_FOLDER_PATH, "bramble.png")
    _BRAMBLE_SELECTED_CAN_CAST_IMAGE = load_image(_IMAGE_FOLDER_PATH, "bramble_selected_can_cast.png")
    _BRAMBLE_SELECTED_CANNOT_CAST_IMAGE = load_image(_IMAGE_FOLDER_PATH, "bramble_selected_cannot_cast.png")
    _BRAMBLE_SELECTED_CANNOT_CAST_IMAGE_MASK = ImageDetection.create_mask(_BRAMBLE_SELECTED_CANNOT_CAST_IMAGE)
    _BRAMBLE_ON_COOLDOWN_IMAGE = load_image(_IMAGE_FOLDER_PATH, "bramble_on_cooldown.png")
    _BRAMBLE_ON_COOLDOWN_IMAGE_MASK = ImageDetection.create_mask(_BRAMBLE_ON_COOLDOWN_IMAGE)

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

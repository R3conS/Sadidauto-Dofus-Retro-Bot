from functools import wraps
from time import perf_counter

import cv2
import pyautogui as pyag

from src.utilities import load_image
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture
from .status_enum import Status


def __get_spell_name(decorated_method_name):
    """Utility function for decorators."""
    names = ["earthquake", "poisoned_wind", "sylvan_power"]
    for name in names:
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


def _get_spell_pos(decorated_method):
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
        images = [
            getattr(cls, f"{spell_name}_selected_cannot_cast_image"),
            getattr(cls, f"{spell_name}_selected_can_cast_image")
        ]
        masks = [
            getattr(cls, f"{spell_name}_selected_cannot_cast_image_mask"),
            getattr(cls, f"{spell_name}_selected_can_cast_image_mask")
        ]
        for image, mask in zip(images, masks):
            if len(
                ImageDetection.find_image(
                    haystack=screenshot,
                    needle=image,
                    confidence=0.98,
                    method=cv2.TM_CCORR_NORMED,
                    mask=mask
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
                confidence=0.98,
                method=cv2.TM_CCORR_NORMED,
                mask=getattr(cls, f"{spell_name}_selected_can_cast_image_mask"),
            )
        ) > 0
    return wrapper


def _select_spell(decorated_method):
    @wraps(decorated_method)
    def wrapper(cls, *args, **kwargs):
        # Making sure to deselect any other spells just in case. Otherwise
        # the can/cannot cast image might block one of the spell icon 
        # images and the get_spell_pos() might return None causing this
        # whole method to fail.
        pyag.moveTo(929, 752)
        pyag.click()

        spell_name = __get_spell_name(decorated_method.__name__)
        spell_pos = getattr(cls, f"get_{spell_name}_pos")()
        if spell_pos is None:
            return Status.FAILED_TO_GET_SPELL_POS
        
        pyag.moveTo(*spell_pos)
        pyag.click()

        # Checking within a timer to give the game time to draw the
        # can cast/cannot cast image once spell pos is clicked.
        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if getattr(cls, f"is_{spell_name}_selected")():
                return Status.SUCCESSFULLY_SELECTED_SPELL
        return Status.FAILED_TO_SELECT_SPELL
    return wrapper

class Spells:

    spell_bar_area = (643, 658, 291, 99)
    image_folder_path = "src\\bot\\states\\in_combat\\sub_state\\fighting\\images\\spells"
    # Earthquake
    earthquake_image = load_image(image_folder_path, "earthquake.png")
    earthquake_selected_can_cast_image = load_image(image_folder_path, "earthquake_selected_can_cast.png")
    earthquake_selected_can_cast_image_mask = ImageDetection.create_mask(earthquake_selected_can_cast_image)
    earthquake_selected_cannot_cast_image = load_image(image_folder_path, "earthquake_selected_cannot_cast.png")
    earthquake_selected_cannot_cast_image_mask = ImageDetection.create_mask(earthquake_selected_cannot_cast_image)
    earthquake_on_cooldown_image = load_image(image_folder_path, "earthquake_on_cooldown.png")
    earthquake_on_cooldown_image_mask = ImageDetection.create_mask(earthquake_on_cooldown_image)
    # Poisoned Wind
    poisoned_wind_image = load_image(image_folder_path, "poisoned_wind.png")
    poisoned_wind_selected_can_cast_image = load_image(image_folder_path, "poisoned_wind_selected_can_cast.png")
    poisoned_wind_selected_can_cast_image_mask = ImageDetection.create_mask(poisoned_wind_selected_can_cast_image)
    poisoned_wind_selected_cannot_cast_image = load_image(image_folder_path, "poisoned_wind_selected_cannot_cast.png")
    poisoned_wind_selected_cannot_cast_image_mask = ImageDetection.create_mask(poisoned_wind_selected_cannot_cast_image)
    poisoned_wind_on_cooldown_image = load_image(image_folder_path, "poisoned_wind_on_cooldown.png")
    poisoned_wind_on_cooldown_image_mask = ImageDetection.create_mask(poisoned_wind_on_cooldown_image)
    # Sylvan Power
    sylvan_power_image = load_image(image_folder_path, "sylvan_power.png")
    sylvan_power_selected_can_cast_image = load_image(image_folder_path, "sylvan_power_selected_can_cast.png")
    sylvan_power_selected_can_cast_image_mask = ImageDetection.create_mask(sylvan_power_selected_can_cast_image)
    sylvan_power_selected_cannot_cast_image = load_image(image_folder_path, "sylvan_power_selected_cannot_cast.png")
    sylvan_power_selected_cannot_cast_image_mask = ImageDetection.create_mask(sylvan_power_selected_cannot_cast_image)
    sylvan_power_on_cooldown_image = load_image(image_folder_path, "sylvan_power_on_cooldown.png")
    sylvan_power_on_cooldown_image_mask = ImageDetection.create_mask(sylvan_power_on_cooldown_image)

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
    @_get_spell_pos
    def get_earthquake_pos(cls):
        pass

    @classmethod
    @_get_spell_pos
    def get_poisoned_wind_pos(cls):
        pass

    @classmethod
    @_get_spell_pos
    def get_sylvan_power_pos(cls):
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
    @_is_spell_castable_on_pos
    def is_earthquake_castable_on_pos(cls, x, y):
        """For accurate results make sure the spell is selected."""
        pass

    @classmethod
    @_is_spell_castable_on_pos
    def is_poisoned_wind_castable_on_pos(cls, x, y):
        """For accurate results make sure the spell is selected"""
        pass

    @classmethod
    @_is_spell_castable_on_pos
    def is_sylvan_power_castable_on_pos(cls, x, y):
        """For accurate results make sure the spell is selected"""
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

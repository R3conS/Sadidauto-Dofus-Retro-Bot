from functools import wraps

import cv2
import pyautogui as pyag

from src.utilities import load_image
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture


def __get_spell_name(decorated_method_name):
    """Utility function for decorators."""
    first_underscore_index = decorated_method_name.index("_")
    last_underscore_index = decorated_method_name.rindex("_")
    return decorated_method_name[first_underscore_index + 1:last_underscore_index]


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
        rectangle = ImageDetection.find_image(
            haystack=ScreenCapture.custom_area(cls.spell_bar_area),
            needle=getattr(cls, f"{__get_spell_name(decorated_method.__name__)}_image"),
            confidence=0.99,
            method=cv2.TM_SQDIFF_NORMED,
        )
        if len(rectangle) > 0:
            return ImageDetection.get_rectangle_center_point((
                rectangle[0] + cls.spell_bar_area[0],
                rectangle[1] + cls.spell_bar_area[1],
                rectangle[2],
                rectangle[3]
            ))
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


class Spells:

    spell_bar_area = (643, 658, 291, 99)
    image_folder_path = "src\\bot\\states\\in_combat\\sub_state\\fighting\\images\\spells"
    earthquake_image = load_image(image_folder_path, "earthquake.png")
    earthquake_selected_can_cast_image = load_image(image_folder_path, "earthquake_selected_can_cast.png")
    earthquake_selected_can_cast_image_mask = ImageDetection.create_mask(earthquake_selected_can_cast_image)
    earthquake_selected_cannot_cast_image = load_image(image_folder_path, "earthquake_selected_cannot_cast.png")
    earthquake_selected_cannot_cast_image_mask = ImageDetection.create_mask(earthquake_selected_cannot_cast_image)
    poisoned_wind_image = load_image(image_folder_path, "poisoned_wind.png")
    poisoned_wind_selected_can_cast_image = load_image(image_folder_path, "poisoned_wind_selected_can_cast.png")
    poisoned_wind_selected_can_cast_image_mask = ImageDetection.create_mask(poisoned_wind_selected_can_cast_image)
    poisoned_wind_selected_cannot_cast_image = load_image(image_folder_path, "poisoned_wind_selected_cannot_cast.png")
    poisoned_wind_selected_cannot_cast_image_mask = ImageDetection.create_mask(poisoned_wind_selected_cannot_cast_image)
    sylvan_power_image = load_image(image_folder_path, "sylvan_power.png")
    sylvan_power_selected_can_cast_image = load_image(image_folder_path, "sylvan_power_selected_can_cast.png")
    sylvan_power_selected_can_cast_image_mask = ImageDetection.create_mask(sylvan_power_selected_can_cast_image)
    sylvan_power_selected_cannot_cast_image = load_image(image_folder_path, "sylvan_power_selected_cannot_cast.png")
    sylvan_power_selected_cannot_cast_image_mask = ImageDetection.create_mask(sylvan_power_selected_cannot_cast_image)

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

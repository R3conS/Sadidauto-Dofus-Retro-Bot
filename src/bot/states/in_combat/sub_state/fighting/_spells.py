from functools import wraps

import cv2

from src.utilities import load_image
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture


def is_spell_available(decorated_method):
    @wraps(decorated_method)
    def wrapper(cls, *args, **kwargs):
        first_underscore_index = decorated_method.__name__.index("_")
        last_underscore_index = decorated_method.__name__.rindex("_")
        spell_name = decorated_method.__name__[first_underscore_index + 1:last_underscore_index]
        return len(
            ImageDetection.find_image(
                haystack=ScreenCapture.custom_area(cls.spell_bar_area),
                needle=getattr(cls, f"{spell_name}_image"),
                confidence=0.99,
                method=cv2.TM_CCORR_NORMED,
                mask=getattr(cls, f"{spell_name}_image_mask")
            )
        ) > 0
    return wrapper


def get_spell_pos(decorated_method):
    @wraps(decorated_method)
    def wrapper(cls, *args, **kwargs):
        first_underscore_index = decorated_method.__name__.index("_")
        last_underscore_index = decorated_method.__name__.rindex("_")
        spell_name = decorated_method.__name__[first_underscore_index + 1:last_underscore_index]
        rectangle = ImageDetection.find_image(
            haystack=ScreenCapture.custom_area(cls.spell_bar_area),
            needle=getattr(cls, f"{spell_name}_image"),
            confidence=0.99,
            method=cv2.TM_CCORR_NORMED,
            mask=getattr(cls, f"{spell_name}_image_mask")
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


class Spells:

    spell_bar_area = (643, 658, 291, 99)
    image_folder_path = "src\\bot\\states\\in_combat\\sub_state\\fighting\\images\\spells"
    earthquake_image = load_image(image_folder_path, "earthquake.png")
    earthquake_image_mask = ImageDetection.create_mask(earthquake_image)
    poisoned_wind_image = load_image(image_folder_path, "poisoned_wind.png")
    poisoned_wind_image_mask = ImageDetection.create_mask(poisoned_wind_image)
    sylvan_power_image = load_image(image_folder_path, "sylvan_power.png")
    sylvan_power_image_mask = ImageDetection.create_mask(sylvan_power_image)

    @classmethod
    @is_spell_available
    def is_earthquake_available(cls):
        pass
    
    @classmethod
    @is_spell_available
    def is_poisoned_wind_available(cls):
        pass
    
    @classmethod
    @is_spell_available
    def is_sylvan_power_available(cls):
        pass

    @classmethod
    @get_spell_pos
    def get_earthquake_pos(cls):
        pass

    @classmethod
    @get_spell_pos
    def get_poisoned_wind_pos(cls):
        pass

    @classmethod
    @get_spell_pos
    def get_sylvan_power_pos(cls):
        pass

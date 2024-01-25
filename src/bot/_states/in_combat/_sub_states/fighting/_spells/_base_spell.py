from src.logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import glob
import os
from time import perf_counter

import cv2
import pyautogui as pyag

from src.utilities.image_detection import ImageDetection
from src.utilities.screen_capture import ScreenCapture
from src.utilities.general import move_mouse_off_game_area, load_image_full_path
from src.bot._states.in_combat._sub_states.fighting._spells._exceptions import (
    FailedToCastSpell,
    FailedToGetSpellIconPosition, 
    FailedToDetectIfSpellIsSelected,
    SpellIsNotCastableOnProvidedPosition,
    FailedToDetectIfSpellWasCastSuccessfully
)


class BaseSpell:

    SPELL_BAR_AREA = (643, 658, 291, 99)
    AP_AREA = (456, 611, 29, 25)

    def __init__(self, name: str, image_folder_path: str):
        self._name = name.title()
        self._image_folder_path = image_folder_path
        self._available_images_loaded = self._load_images("available")
        self._on_cooldown_images_loaded = self._load_images("on_cooldown")
        self._on_cooldown_image_masks = ImageDetection.create_masks(self._on_cooldown_images_loaded)
        self._selected_can_cast_images_loaded = self._load_images("selected_can_cast")
        self._selected_cannot_cast_images_loaded = self._load_images("selected_cannot_cast")
        self._selected_cannot_cast_image_masks = ImageDetection.create_masks(self._selected_cannot_cast_images_loaded)

    def is_available(self):
        return len(
            ImageDetection.find_images(
                haystack=ScreenCapture.custom_area(self.SPELL_BAR_AREA),
                needles=self._available_images_loaded,
                confidence=0.99,
                method=cv2.TM_SQDIFF_NORMED,
            )
        ) > 0

    def get_icon_pos(self):
        # Note:
        # Returning the top left corner instead of the center to prevent
        # parts of the spell image from being cut off by the bottom of 
        # the game window. If the center is returned and select() is 
        # called while the spell is on the second row of the spell bar,
        # the is_selected() method will always return False because
        # the images will only be partially visible.
        haystack = ScreenCapture.custom_area(self.SPELL_BAR_AREA)
        
        rectangles = ImageDetection.find_images(
            haystack=haystack,
            needles=self._available_images_loaded,
            confidence=0.98,
            method=cv2.TM_SQDIFF_NORMED
        )
        if len(rectangles) > 0:
            return rectangles[0][0] + self.SPELL_BAR_AREA[0], rectangles[0][1] + self.SPELL_BAR_AREA[1]
        
        rectangles = ImageDetection.find_images(
            haystack=haystack,
            needles=self._on_cooldown_images_loaded,
            confidence=0.98,
            method=cv2.TM_CCORR_NORMED,
            masks=self._on_cooldown_image_masks
        )
        if len(rectangles) > 0:
            return rectangles[0][0] + self.SPELL_BAR_AREA[0], rectangles[0][1] + self.SPELL_BAR_AREA[1]
        
        return None

    def is_selected(self):
        haystack = ScreenCapture.around_pos(pyag.position(), 75)
        if len(
            ImageDetection.find_images(
                haystack=haystack,
                needles=self._selected_can_cast_images_loaded,
                confidence=0.98,
                method=cv2.TM_SQDIFF_NORMED
            )
        ) > 0:
            return True
        if len(
            ImageDetection.find_images(
                haystack=haystack,
                needles=self._selected_cannot_cast_images_loaded,
                confidence=0.98,
                method=cv2.TM_CCORR_NORMED,
                masks=self._selected_cannot_cast_image_masks
            )
        ) > 0:
            return True
        return False

    def is_castable_on_pos(self, x, y):
        pyag.moveTo(x, y)
        return len(
            ImageDetection.find_images(
                haystack=ScreenCapture.around_pos((x, y), 75),
                needles=self._selected_can_cast_images_loaded,
                confidence=0.97,
                method=cv2.TM_SQDIFF_NORMED
            )
        ) > 0

    def select(self):
        log.info(f"Selecting '{self._name}' spell ... ")
        # Making sure to deselect any other spells just in case. Otherwise
        # the can/cannot cast image might block one of the spell icon 
        # images and the get_spell_icon_pos() might return None causing this
        # whole method to fail.
        move_mouse_off_game_area()
        pyag.click()

        icon_pos = self.get_icon_pos()
        if icon_pos is None:
            raise FailedToGetSpellIconPosition(f"Failed to get '{self._name}' spell icon position.")
        
        pyag.moveTo(*icon_pos)
        pyag.click()

        # Checking within a timer to give the game time to draw the
        # can cast/cannot cast image once spell pos is clicked.
        timeout = 5
        start_time = perf_counter()
        while perf_counter() - start_time <= timeout:
            if self.is_selected():
                log.info(f"Successfully selected '{self._name}' spell.")
                return
            
        raise FailedToDetectIfSpellIsSelected(
            f"Failed to detect if '{self._name}' spell was selected. Timed out: {timeout} seconds."
        )

    def cast(self, x, y):
        log.info(f"Attempting to cast: '{self._name}' ... ")

        try:
            self.select()
        
            if not self.is_castable_on_pos(x, y):
                raise SpellIsNotCastableOnProvidedPosition(f"Spell is not castable on position: {x, y}.")

            log.info(f"Casting ... ")
            ap_area_before_casting = ScreenCapture.custom_area(self.AP_AREA)
            pyag.click() # No need to move before clicking because is_castable_on_pos() already does that.
            
            timeout = 5
            start_time = perf_counter()
            while perf_counter() - start_time <= timeout:
                ap_area_after_casting = ScreenCapture.custom_area(self.AP_AREA)
                rectangle = ImageDetection.find_image(
                    haystack=ap_area_after_casting,
                    needle=ap_area_before_casting,
                    confidence=0.98,
                    method=cv2.TM_CCOEFF_NORMED,
                )
                if len(rectangle) <= 0: # If images are different then the spell animation has finished.
                    log.info(f"Successfully cast: '{self._name}'.")
                    # Making sure the cursor doesn't remain on the casting position
                    # because it might hover over the character or monster and
                    # make the info card appear.
                    move_mouse_off_game_area() 
                    return
            
            raise FailedToDetectIfSpellWasCastSuccessfully(
                f"Timed out while detecting if '{self._name}' was cast successfully. "
                f"Timeout: {timeout} seconds."
            )
        
        except (FailedToGetSpellIconPosition, FailedToDetectIfSpellIsSelected):
            raise FailedToCastSpell(f"Failed to cast '{self._name}' because it couldn't be selected.")
        except SpellIsNotCastableOnProvidedPosition:
            raise FailedToCastSpell(f"Failed to cast '{self._name}' because it is not castable on provided position: {x, y}.")
        except FailedToDetectIfSpellWasCastSuccessfully:
            raise FailedToCastSpell(f"Failed to cast '{self._name}' because couldn't detect if spell animation has finished.")
        finally:
            # To make sure the vision of spell bar is not blocked for any
            # subsequent cast attempts.
            move_mouse_off_game_area() 

    def _load_images(self, sub_folder_name: str):
        image_folder = os.path.join(self._image_folder_path, sub_folder_name)
        if not os.path.exists(image_folder):
            raise ValueError(f"Image folder '{image_folder}' does not exist.")
        if not os.path.isdir(image_folder):
            raise ValueError(f"Path '{image_folder}' is not a directory.")
        
        image_paths = glob.glob(os.path.join(image_folder, "*.png"))
        if len(image_paths) == 0:
            raise ValueError(f"Image folder '{image_folder}' must contain at least one image.")
        return [load_image_full_path(path) for path in image_paths]

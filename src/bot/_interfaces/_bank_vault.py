from src.logger import get_logger

log = get_logger()

import os
from time import perf_counter

import cv2
import pyautogui as pyag

from src.bot._exceptions import RecoverableException
from src.bot._interfaces._interface import Interface
from src.bot._states.out_of_combat._sub_states.banking.bank_data import Getter as BankDataGetter
from src.utilities.general import load_image
from src.utilities.image_detection import ImageDetection
from src.utilities.ocr.ocr import OCR
from src.utilities.screen_capture import ScreenCapture


class BankVault:
    """Bank vault interface."""

    def __init__(self, script: str, game_window_title: str):
        self._script = script
        self._game_window_title = game_window_title
        self._banker_npc_images_loaded =  self._load_npc_images(
            BankDataGetter.get_data(self._script)["npc_image_folder_path"]
        )
        self._name = "Bank Vault"
        self._interface = Interface(self._name)

    def open(self):
        if self.is_open():
            return
        self._talk_with_banker(*self._get_banker_npc_coords())
        self._select_consult_your_personal_safe()
        self._wait_item_sprites_loaded()
        log.info("Successfully opened 'Bank Vault' interface.")

    def close(self):
        return self._interface.close(904, 172, self.is_open)

    @staticmethod
    def is_open():
        return all((
            pyag.pixelMatchesColor(218, 170, (81, 74, 60)),
            pyag.pixelMatchesColor(881, 172, (81, 74, 60)),
            pyag.pixelMatchesColor(700, 577, (213, 207, 170)),
            pyag.pixelMatchesColor(31, 568, (213, 207, 170)),
        ))

    def _get_banker_npc_coords(self):
        log.info("Getting banker NPC coordinates ... ")
        rectangles = ImageDetection.find_images(
            haystack=ScreenCapture.game_window(),
            needles=self._banker_npc_images_loaded,
            confidence=0.99,
            method=cv2.TM_CCORR_NORMED
        )
        if len(rectangles) > 0:
            log.info("Successfully got banker NPC coordinates.")
            return ImageDetection.get_rectangle_center_point(rectangles[0])
        raise RecoverableException("Failed to get banker NPC coordinates.")

    def _talk_with_banker(self, banker_x, banker_y,):
        log.info("Talking with banker ... ")
        if "Dofus Retro" in self._game_window_title:
            pyag.moveTo(banker_x, banker_y)
            pyag.click(button="right")
        else: # For Abrak private server
            pyag.keyDown("shift")
            pyag.moveTo(banker_x, banker_y)
            pyag.click()
            pyag.keyUp("shift")

        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if self.is_banker_dialogue_open():
                log.info("Successfully talked with banker.")
                return
        raise RecoverableException("Failed to open banker dialogue.")

    @staticmethod
    def is_banker_dialogue_open():
        text = OCR.get_text_from_image(ScreenCapture.custom_area((0, 213, 453, 264)))
        return "Consult your personal safe" in text or "End dialogue" in text

    @classmethod
    def _select_consult_your_personal_safe(cls):
        """Selects the 'Consult your personal safe' option from the banker dialogue."""
        log.info("Selecting 'Consult your personal safe' option from the banker dialogue ...")
        pyag.moveTo(294, 365)
        pyag.click()
        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if cls.is_open():
                log.info("Successfully selected 'Consult your personal safe' option from the banker dialogue.")
                return
        raise RecoverableException("Failed to select 'Consult your personal safe' option from the banker dialogue.")

    @staticmethod
    def _wait_item_sprites_loaded():
        """
        Checks for the character's name in the inventory title bar.
        When it's displayed it means the sprites have loaded.
        """
        log.info("Waiting for item sprites to load ...")
        start_time = perf_counter()
        timeout = 5
        while perf_counter() - start_time <= timeout:
            bar = ScreenCapture.custom_area((684, 159, 210, 27))
            bar = OCR.convert_to_grayscale(bar)
            bar = OCR.resize_image(bar, bar.shape[1] * 2, bar.shape[0] * 3)
            bar = OCR.invert_image(bar)
            bar = OCR.binarize_image(bar, 127)
            if len(OCR.get_text_from_image(bar)) > 0:
                log.info("Item sprites have loaded.")
                return
        raise RecoverableException(
            "Failed to detect if item sprites have loaded."
            f"Timeout: '{timeout}' seconds."
        )

    @staticmethod
    def _load_npc_images(image_folder_path: str):
        if not os.path.exists(image_folder_path):
            raise Exception(f"Image folder path '{image_folder_path}' does not exist.")
        if not os.path.isdir(image_folder_path):
            raise Exception(f"Image folder path '{image_folder_path}' is not a directory.")
        return [load_image(image_folder_path, image) for image in os.listdir(image_folder_path)]

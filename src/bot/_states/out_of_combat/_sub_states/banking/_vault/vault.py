from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import os
from time import perf_counter

import cv2
import pyautogui as pyag

from ._tabs.equipment_tab import EquipmentTab
from ._tabs.miscellaneous_tab import MiscellaneousTab
from ._tabs.resources_tab import ResourcesTab
from src.utilities import load_image
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture
from src.bot._states.out_of_combat._status_enum import Status
from src.ocr.ocr import OCR
from src.bot._states.out_of_combat._sub_states.banking._bank_data import Getter as BankData
from src.bot._exceptions import RecoverableException


class Vault:

    EQUIPMENT_TAB = EquipmentTab()
    MISCELLANEOUS_TAB = MiscellaneousTab()
    RESOURCES_TAB = ResourcesTab()

    def __init__(self, script: str, game_window_title: str):
        self._script = script
        self._game_window_title = game_window_title
        self._banker_npc_images_loaded =  self._load_npc_images(BankData.get_data(self._script)["npc_image_folder_path"])

    def open_vault(self):
        if self.is_vault_open():
            return
        self._detect_banker_npc()
        banker_coords = self._get_banker_npc_coords()
        self._talk_with_banker(banker_coords[0], banker_coords[1])
        self._select_consult_your_personal_safe()
        self._have_item_sprites_loaded()

    @classmethod
    def close_vault(cls):
        log.info("Closing the bank vault ... ")
        pyag.moveTo(904, 172)
        pyag.click()
        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if not cls.is_vault_open():
                log.info("Successfully closed the bank vault.")
                return
        raise RecoverableException("Failed to close the bank vault.")

    @classmethod
    def deposit_all_tabs(cls):
        log.info("Depositing all tabs ... ")
        cls.EQUIPMENT_TAB.deposit_tab()
        cls.MISCELLANEOUS_TAB.deposit_tab()
        cls.RESOURCES_TAB.deposit_tab()
        log.info("Successfully deposited all tabs.")

    def _detect_banker_npc(self):
        log.info("Detecting banker NPC ... ")
        rectangles = ImageDetection.find_images(
            haystack=ScreenCapture.game_window(),
            needles=self._banker_npc_images_loaded,
            confidence=0.99,
            method=cv2.TM_CCORR_NORMED
        )
        if len(rectangles) > 0:
            log.info("Successfully detected banker NPC.")
            return
        raise RecoverableException("Failed to detect banker NPC.")

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
            if self._is_banker_dialogue_open():
                log.info("Successfully talked with banker.")
                return
        raise RecoverableException("Failed to open banker dialogue.")

    @classmethod
    def _select_consult_your_personal_safe(cls):
        """Selects the 'Consult your personal safe' option from the banker dialogue."""
        log.info("Selecting 'Consult your personal safe' option from the banker dialogue ...")
        pyag.moveTo(294, 365)
        pyag.click()
        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if cls.is_vault_open():
                log.info("Successfully selected 'Consult your personal safe' option from the banker dialogue.")
                return
        raise RecoverableException("Failed to select 'Consult your personal safe' option from the banker dialogue.")

    @staticmethod
    def _is_banker_dialogue_open():
        """Astrub banker dialogue interface."""
        if all((
            pyag.pixelMatchesColor(25, 255, (255, 255, 206)),
            pyag.pixelMatchesColor(123, 255, (255, 255, 206))
        )): 
            return True
        return False

    @staticmethod
    def is_vault_open():
        if all ((
            pyag.pixelMatchesColor(218, 170, (81, 74, 60)),
            pyag.pixelMatchesColor(881, 172, (81, 74, 60)),
            pyag.pixelMatchesColor(700, 577, (213, 207, 170)),
            pyag.pixelMatchesColor(31, 568, (213, 207, 170)),
        )):
            return True
        return False

    @staticmethod
    def _have_item_sprites_loaded():
        """
        Checks for the character's name in the inventory title bar.
        When it's displayed it means the sprites have loaded.
        """
        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            bar = ScreenCapture.custom_area((684, 159, 210, 27))
            bar = OCR.convert_to_grayscale(bar)
            bar = OCR.resize_image(bar, bar.shape[1] * 2, bar.shape[0] * 3)
            bar = OCR.invert_image(bar)
            bar = OCR.binarize_image(bar, 127)
            if len(OCR.get_text_from_image(bar)) > 0:
                log.info("Successfully detected if item sprites have loaded.")
                return
        log.error("Timed out while detecting if item sprites have loaded.")
        raise RecoverableException("Failed to detect if item sprites have loaded.")

    @staticmethod
    def _load_npc_images(image_folder_path: str):
        if not os.path.exists(image_folder_path):
            raise Exception(f"Image folder path '{image_folder_path}' does not exist.")
        if not os.path.isdir(image_folder_path):
            raise Exception(f"Image folder path '{image_folder_path}' is not a directory.")
        return [load_image(image_folder_path, image) for image in os.listdir(image_folder_path)]

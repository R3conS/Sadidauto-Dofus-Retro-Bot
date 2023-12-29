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
from src.bot.states.out_of_combat.status_enum import Status
from src.ocr.ocr import OCR
from src.bot.states.out_of_combat.sub_state.banking._bank_data import Getter as BankData


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
            return Status.SUCCESSFULLY_OPENED_BANK_VAULT

        result = self._detect_banker_npc()
        if result != Status.SUCCESSFULLY_DETECTED_BANKER_NPC:
            return result

        banker_coords = self._get_banker_npc_coords()
        if banker_coords is None:
            # ToDo: Add a way to handle this error and make a custom exception for it.
            raise Exception("Failed to get banker NPC coordinates.")

        result = self._talk_with_banker(banker_coords[0], banker_coords[1])
        if result != Status.SUCCESSFULLY_OPENED_BANKER_DIALOGUE:
            return result
        
        result = self._select_consult_your_personal_safe()
        if result != Status.SUCCESSFULLY_SELECTED_CONSULT_YOUR_PERSONAL_SAFE:
            return result

        result = self._have_item_sprites_loaded()
        if result != Status.SUCCESSFULLY_DETECTED_IF_ITEM_SPRITES_HAVE_LOADED:
            return result

        return Status.SUCCESSFULLY_OPENED_BANK_VAULT

    @classmethod
    def close_vault(cls):
        log.info("Closing the bank vault ... ")
        pyag.moveTo(904, 172)
        pyag.click()
        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if not cls.is_vault_open():
                log.info("Successfully closed the bank vault.")
                return Status.SUCCESSFULLY_CLOSED_BANK_VAULT
        log.error("Failed to close the bank vault.")
        return Status.FAILED_TO_CLOSE_BANK_VAULT

    @classmethod
    def deposit_all_tabs(cls):
        log.info("Depositing all tabs ... ")
        deposit_methods = [
            cls.EQUIPMENT_TAB.deposit_tab,
            cls.MISCELLANEOUS_TAB.deposit_tab,
            cls.RESOURCES_TAB.deposit_tab,
        ]
        for deposit_method in deposit_methods:
            status = deposit_method()
            if (
                status == Status.FAILED_TO_OPEN_TAB 
                or status == Status.FAILED_TO_DEPOSIT_ITEMS_IN_TAB
                or status == Status.FAILED_TO_DEPOSIT_SLOT
                or status == Status.FAILED_TO_GET_OCCUPIED_BANK_PODS
            ):
                log.error("Failed to deposit all tabs.")
                return Status.FAILED_TO_DEPOSIT_ALL_TABS
        log.info("Successfully deposited all tabs.")
        return Status.SUCCESSFULLY_DEPOSITED_ALL_TABS

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
            return Status.SUCCESSFULLY_DETECTED_BANKER_NPC
        log.error("Failed to detect banker NPC.")
        return Status.FAILED_TO_DETECT_BANKER_NPC

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
        log.error("Failed to get banker NPC coordinates.")
        return None

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
                return Status.SUCCESSFULLY_OPENED_BANKER_DIALOGUE
        log.error("Failed to talk with banker.")
        return Status.FAILED_TO_OPEN_BANKER_DIALOGUE

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
                return Status.SUCCESSFULLY_SELECTED_CONSULT_YOUR_PERSONAL_SAFE
        log.error("Failed to select 'Consult your personal safe' option from the banker dialogue.")
        return Status.FAILED_TO_SELECT_CONSULT_YOUR_PERSONAL_SAFE

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
                return Status.SUCCESSFULLY_DETECTED_IF_ITEM_SPRITES_HAVE_LOADED
        log.error("Timed out while detecting if item sprites have loaded.")
        return Status.FAILED_TO_DETECT_IF_ITEM_SPRITES_HAVE_LOADED

    @staticmethod
    def _load_npc_images(image_folder_path: str):
        if not os.path.exists(image_folder_path):
            raise Exception(f"Image folder path '{image_folder_path}' does not exist.")
        if not os.path.isdir(image_folder_path):
            raise Exception(f"Image folder path '{image_folder_path}' is not a directory.")
        return [load_image(image_folder_path, image) for image in os.listdir(image_folder_path)]

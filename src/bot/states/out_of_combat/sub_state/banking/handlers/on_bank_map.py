from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import os

import pyautogui as pyag
from time import perf_counter

from src.utilities import load_image
from ..status_enum import Status
from .._vault_actions import VaultActions
from src.image_detection import ImageDetection
from src.bot.map_changer.map_changer import MapChanger
from src.ocr.ocr import OCR
from src.screen_capture import ScreenCapture


class Handler:

    _image_folder_path = "src\\bot\\states\\out_of_combat\\sub_state\\banking\\images\\astrub_banker_npc"
    _npc_images = []
    for image in os.listdir(_image_folder_path):
        _npc_images.append(load_image(_image_folder_path, image))

    def __init__(self, game_window_title: str):
        self._game_window_title = game_window_title

    def handle(self):
        if not self._is_char_inside_astrub_bank():
            if self._handle_character_outside_bank() == Status.FAILED_TO_ENTER_BANK:
                return Status.FAILED_TO_ENTER_BANK

        if not self._is_bank_vault_open():
            status = self._handle_vault_closed()
            if (
                status == Status.FAILED_TO_OPEN_BANK_VAULT
                or status == Status.FAILED_TO_OPEN_BANKER_DIALOGUE
                or status == Status.FAILED_TO_DETECT_BANKER_NPC
                or status == Status.FAILED_TO_DETECT_IF_ITEM_SPRITES_HAVE_LOADED
            ):
                return Status.FAILED_TO_OPEN_BANK_VAULT
            
        if self._handle_vault_open() == Status.FAILED_TO_DEPOSIT_ALL_TABS:
            return Status.FAILED_TO_DEPOSIT_ALL_TABS
    
        status = self._handle_finished_depositing()
        if status == Status.FAILED_TO_CLOSE_BANK_VAULT:
            return Status.FAILED_TO_CLOSE_BANK_VAULT
        elif status == Status.FAILED_TO_LEAVE_BANK:
            return Status.FAILED_TO_LEAVE_BANK

    def _handle_character_outside_bank(self):
        log.info("Character is outside the bank. Going inside ... ")
        self._go_into_astrub_bank()
        if MapChanger.has_loading_screen_passed():
            if self._is_char_inside_astrub_bank():
                log.info("Successfully entered the bank.")
                return Status.SUCCESSFULLY_ENTERED_BANK
            else:
                log.error("Failed to enter the bank.")
                return Status.FAILED_TO_ENTER_BANK
        else:
            log.error("Failed to detect loading screen after trying to enter the bank.")
            return Status.FAILED_TO_ENTER_BANK

    def _handle_vault_closed(self):
        if self._is_banker_npc_detected():
            banker_x, banker_y = self._get_banker_npc_coords()
            log.info("Banker NPC detected. Talking with banker ... ")
            self._talk_with_banker(banker_x, banker_y)
            if self._is_banker_dialogue_open():
                log.info("Successfully opened banker dialogue. Opening bank vault ...")
                self._select_consult_your_personal_safe()
                if self._is_bank_vault_open():
                    log.info("Successfully opened bank vault.")
                    log.info("Waiting for item sprites to load ... ")
                    if self._have_item_sprites_loaded():
                        log.info("Item sprites have loaded.")
                        return Status.SUCCESSFULLY_OPENED_BANK_VAULT
                    else:
                        log.error("Failed to detect if item sprites have loaded.")
                        return Status.FAILED_TO_DETECT_IF_ITEM_SPRITES_HAVE_LOADED
                else:
                    log.error("Failed to open bank vault.")
                    return Status.FAILED_TO_OPEN_BANK_VAULT
            else:
                log.error("Failed to open banker dialogue.")
                return Status.FAILED_TO_OPEN_BANKER_DIALOGUE
        else:
            log.error("Failed to detect banker NPC.")
            return Status.FAILED_TO_DETECT_BANKER_NPC
        
    def _handle_vault_open(self):
        return VaultActions.deposit_all_tabs()
    
    def _handle_finished_depositing(self):
        log.info("Closing the bank vault ... ")
        self._close_bank_vault()
        if not self._is_bank_vault_open():
            log.info("Successfully closed the bank vault.")
            log.info("Leaving the bank ... ")
            self._leave_astrub_bank()
            if MapChanger.has_loading_screen_passed():
                if not self._is_char_inside_astrub_bank():
                    log.info("Successfully left the bank.")
                    return Status.SUCCESSFULLY_LEFT_BANK
                else:
                    log.error("Failed to leave the bank.")
                    return Status.FAILED_TO_LEAVE_BANK
            else:
                log.error("Failed to detect loading screen after trying to leave the bank.")
                return Status.FAILED_TO_LEAVE_BANK
        log.error("Failed to close the bank vault.")
        return Status.FAILED_TO_CLOSE_BANK_VAULT

    @staticmethod
    def _is_banker_dialogue_open():
        """Astrub banker dialogue interface."""
        return all((
            pyag.pixelMatchesColor(25, 255, (255, 255, 206)),
            pyag.pixelMatchesColor(123, 255, (255, 255, 206))
        ))

    @staticmethod
    def _is_bank_vault_open():
        return all ((
            pyag.pixelMatchesColor(218, 170, (81, 74, 60)),
            pyag.pixelMatchesColor(881, 172, (81, 74, 60)),
            pyag.pixelMatchesColor(700, 577, (213, 207, 170)),
            pyag.pixelMatchesColor(31, 568, (213, 207, 170)),
        ))

    @classmethod
    def _is_banker_npc_detected(cls):
        astrub_bank_interior = ScreenCapture.game_window()
        for banker_image in cls._npc_images:
            result = ImageDetection.find_image(
                haystack=astrub_bank_interior,
                needle=banker_image,
                confidence=0.99,
            )
            if len(result) > 0:
                return True
        return False
    
    @classmethod
    def _get_banker_npc_coords(cls):
        astrub_bank_interior = ScreenCapture.game_window()
        for banker_image in cls._npc_images:
            result = ImageDetection.find_image(
                haystack=astrub_bank_interior,
                needle=banker_image,
                confidence=0.99,
            )
            if len(result) > 0:
                return ImageDetection.get_rectangle_center_point(result)
        raise ValueError("Failed to find banker npc.")

    def _talk_with_banker(self, banker_x, banker_y):
        if "Dofus Retro" in self._game_window_title:
            pyag.moveTo(banker_x, banker_y)
            pyag.click("right")
        else: # For Abrak private server
            pyag.keyDown("shift")
            pyag.moveTo(banker_x, banker_y)
            pyag.click()
            pyag.keyUp("shift")

        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if self._is_banker_dialogue_open():
                return True
        return False

    @classmethod
    def _select_consult_your_personal_safe(cls):
        """Selects the 'Consult your personal safe' option from the banker dialogue."""
        pyag.moveTo(294, 365)
        pyag.click()

        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if cls._is_bank_vault_open():
                return True
        return False

    @staticmethod
    def _is_char_inside_astrub_bank():
        return all((
            pyag.pixelMatchesColor(10, 587, (0, 0, 0)),
            pyag.pixelMatchesColor(922, 587, (0, 0, 0)),
            pyag.pixelMatchesColor(454, 90, (0, 0, 0)), 
            pyag.pixelMatchesColor(533, 99, (242, 240, 236)),
            pyag.pixelMatchesColor(491, 124, (239, 236, 232))
        ))

    @staticmethod
    def _go_into_astrub_bank():
        pyag.keyDown('e')
        pyag.moveTo(792, 203)
        pyag.click()
        pyag.keyUp('e')

    @classmethod
    def _close_bank_vault(cls):
        pyag.moveTo(904, 172)
        pyag.click()
        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if not cls._is_bank_vault_open():
                return True
        return False

    @staticmethod
    def _leave_astrub_bank():
        pyag.keyDown('e')
        pyag.moveTo(262, 502)
        pyag.click()
        pyag.keyUp('e')

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
                return True
        return False

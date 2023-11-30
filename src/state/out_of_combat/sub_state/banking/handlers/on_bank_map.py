from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import os

import cv2
import pyautogui as pyag
from time import perf_counter

from ..status_enum import Status
from .._vault_actions import VaultActions
from src.detection import Detection
from src.map_changer.map_changer import MapChanger
from src.ocr.ocr import OCR
from src.window_capture import WindowCapture


class Handler:

    def __init__(self, game_window_title: str):
        self.__game_window_title = game_window_title
        self.__npc_images = self.__load_npc_images()

    def handle(self):
        if not self.is_char_inside_astrub_bank():
            if self.handle_character_outside_bank() == Status.FAILED_TO_ENTER_BANK:
                return Status.FAILED_TO_ENTER_BANK

        if not self.is_bank_vault_open():
            status = self.handle_vault_closed()
            if (
                status == Status.FAILED_TO_OPEN_BANK_VAULT
                or status == Status.FAILED_TO_OPEN_BANKER_DIALOGUE
                or status == Status.FAILED_TO_DETECT_BANKER_NPC
                or status == Status.FAILED_TO_DETECT_IF_ITEM_SPRITES_HAVE_LOADED
            ):
                return Status.FAILED_TO_OPEN_BANK_VAULT
            
        if self.handle_vault_open() == Status.FAILED_TO_DEPOSIT_ALL_TABS:
            return Status.FAILED_TO_DEPOSIT_ALL_TABS
    
        status = self.handle_finished_depositing()
        if status == Status.FAILED_TO_CLOSE_BANK_VAULT:
            return Status.FAILED_TO_CLOSE_BANK_VAULT
        elif status == Status.FAILED_TO_LEAVE_BANK:
            return Status.FAILED_TO_LEAVE_BANK

    def handle_character_outside_bank(self):
        log.info("Character is outside the bank. Going inside ... ")
        self.go_into_astrub_bank()
        if MapChanger.has_loading_screen_passed():
            if self.is_char_inside_astrub_bank():
                log.info("Successfully entered the bank.")
                return Status.SUCCESSFULLY_ENTERED_BANK
            else:
                log.info("Failed to enter the bank.")
                return Status.FAILED_TO_ENTER_BANK
        else:
            log.info("Failed to detect loading screen after trying to enter the bank.")
            return Status.FAILED_TO_ENTER_BANK

    def handle_vault_closed(self):
        if self.is_banker_npc_detected():
            banker_x, banker_y = self.get_banker_npc_coords()
            log.info("Banker NPC detected. Talking with banker ... ")
            self.talk_with_banker(banker_x, banker_y)
            if self.is_banker_dialogue_open():
                log.info("Successfully opened banker dialogue. Opening bank vault ...")
                self.select_consult_your_personal_safe()
                if self.is_bank_vault_open():
                    log.info("Successfully opened bank vault.")
                    log.info("Waiting for item sprites to load ... ")
                    if self.have_item_sprites_loaded():
                        log.info("Item sprites have loaded.")
                        return Status.SUCCESSFULLY_OPENED_BANK_VAULT
                    else:
                        log.info("Failed to detect if item sprites have loaded.")
                        return Status.FAILED_TO_DETECT_IF_ITEM_SPRITES_HAVE_LOADED
                else:
                    log.info("Failed to open bank vault.")
                    return Status.FAILED_TO_OPEN_BANK_VAULT
            else:
                log.info("Failed to open banker dialogue.")
                return Status.FAILED_TO_OPEN_BANKER_DIALOGUE
        else:
            log.info("Failed to detect banker NPC.")
            return Status.FAILED_TO_DETECT_BANKER_NPC
        
    def handle_vault_open(self):
        return VaultActions.deposit_all_tabs()
    
    def handle_finished_depositing(self):
        log.info("Closing the bank vault ... ")
        self.close_bank_vault()
        if not self.is_bank_vault_open():
            log.info("Successfully closed the bank vault.")
            log.info("Leaving the bank ... ")
            self.leave_astrub_bank()
            if MapChanger.has_loading_screen_passed():
                if not self.is_char_inside_astrub_bank():
                    log.info("Successfully left the bank.")
                    return Status.SUCCESSFULLY_LEFT_BANK
                else:
                    log.info("Failed to leave the bank.")
                    return Status.FAILED_TO_LEAVE_BANK
            else:
                log.info("Failed to detect loading screen after trying to leave the bank.")
                return Status.FAILED_TO_LEAVE_BANK
        log.info("Failed to close the bank vault.")
        return Status.FAILED_TO_CLOSE_BANK_VAULT

    @staticmethod
    def is_banker_dialogue_open():
        """Astrub banker dialogue interface."""
        return all((
            pyag.pixelMatchesColor(25, 255, (255, 255, 206)),
            pyag.pixelMatchesColor(123, 255, (255, 255, 206))
        ))

    @staticmethod
    def is_bank_vault_open():
        return all ((
            pyag.pixelMatchesColor(218, 170, (81, 74, 60)),
            pyag.pixelMatchesColor(881, 172, (81, 74, 60)),
            pyag.pixelMatchesColor(700, 577, (213, 207, 170)),
            pyag.pixelMatchesColor(31, 568, (213, 207, 170)),
        ))

    def is_banker_npc_detected(self):
        astrub_bank_interior = WindowCapture.gamewindow_capture()
        for banker_image in self.__npc_images:
            result = Detection.find_image(
                haystack=astrub_bank_interior,
                needle=banker_image,
                confidence=0.99,
            )
            if len(result) > 0:
                return True
        return False
    
    def get_banker_npc_coords(self):
        astrub_bank_interior = WindowCapture.gamewindow_capture()
        for banker_image in self.__npc_images:
            result = Detection.find_image(
                haystack=astrub_bank_interior,
                needle=banker_image,
                confidence=0.99,
            )
            if len(result) > 0:
                return Detection.get_rectangle_center_point(result)
        raise ValueError("Failed to find banker npc.")

    def talk_with_banker(self, banker_x, banker_y):
        if "Dofus Retro" in self.__game_window_title:
            pyag.moveTo(banker_x, banker_y)
            pyag.click("right")
        else: # For Abrak private server
            pyag.keyDown("shift")
            pyag.moveTo(banker_x, banker_y)
            pyag.click()
            pyag.keyUp("shift")

        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if self.is_banker_dialogue_open():
                return True
        return False

    @classmethod
    def select_consult_your_personal_safe(cls):
        """Selects the 'Consult your personal safe' option from the banker dialogue."""
        pyag.moveTo(294, 365)
        pyag.click()

        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if cls.is_bank_vault_open():
                return True
        return False

    def __load_npc_images(self):
        image_folder_path = "src\\state\\out_of_combat\\sub_state\\banking\\images\\astrub_banker_npc"
        loaded_images = []
        for image in os.listdir(image_folder_path):
            loaded_images.append(cv2.imread(os.path.join(image_folder_path, image), cv2.IMREAD_UNCHANGED))
        return loaded_images

    @staticmethod
    def is_char_inside_astrub_bank():
        return all((
            pyag.pixelMatchesColor(10, 587, (0, 0, 0)),
            pyag.pixelMatchesColor(922, 587, (0, 0, 0)),
            pyag.pixelMatchesColor(454, 90, (0, 0, 0)), 
            pyag.pixelMatchesColor(533, 99, (242, 240, 236)),
            pyag.pixelMatchesColor(491, 124, (239, 236, 232))
        ))

    @staticmethod
    def go_into_astrub_bank():
        pyag.keyDown('e')
        pyag.moveTo(792, 203)
        pyag.click()
        pyag.keyUp('e')

    @classmethod
    def close_bank_vault(cls):
        pyag.moveTo(904, 172)
        pyag.click()
        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            if not cls.is_bank_vault_open():
                return True
        return False

    @staticmethod
    def leave_astrub_bank():
        pyag.keyDown('e')
        pyag.moveTo(262, 502)
        pyag.click()
        pyag.keyUp('e')

    @staticmethod
    def have_item_sprites_loaded():
        """
        Checks for the character's name in the inventory title bar.
        When it's displayed it means the sprites have loaded.
        """
        start_time = perf_counter()
        while perf_counter() - start_time <= 5:
            bar = WindowCapture.custom_area_capture((684, 159, 210, 27))
            bar = OCR.convert_to_grayscale(bar)
            bar = OCR.resize_image(bar, bar.shape[1] * 2, bar.shape[0] * 3)
            bar = OCR.invert_image(bar)
            bar = OCR.binarize_image(bar, 127)
            if len(OCR.get_text_from_image(bar, ocr_engine="tesserocr")) > 0:
                return True
        return False

from src.logger import Logger
log = Logger.get_logger(Logger.DEBUG, True, True)

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


class BankerDialogue:
    """Banker dialogue interface."""

    def __init__(self, script: str, game_window_title: str):
        self._script = script
        self._game_window_title = game_window_title
        self._banker_npc_images_loaded =  self._load_npc_images(
            BankDataGetter.get_data(self._script)["npc_image_folder_path"]
        )
        self._name = "Banker Dialogue"
        self._interface = Interface(self._name)

    def open(self):
        if self.is_open():
            return
        self._detect_npc()
        banker_coords = self._get_npc_coords()
        self._talk_with_npc(banker_coords[0], banker_coords[1])
        log.info("Successfully opened 'Banker Dialogue' interface.")

    def close(self):
        return self._interface.close(423, 235, self.is_open)

    @staticmethod
    def is_open():
        text = OCR.get_text_from_image(ScreenCapture.custom_area((0, 213, 453, 264)))
        return "Consult your personal safe" in text or "End dialogue" in text

    def _detect_npc(self):
        log.info("Detecting banker NPC ... ")
        if len(
            ImageDetection.find_images(
                haystack=ScreenCapture.game_window(),
                needles=self._banker_npc_images_loaded,
                confidence=0.99,
                method=cv2.TM_CCORR_NORMED
            )
        ) > 0:
            log.info("Successfully detected banker NPC.")
            return
        raise RecoverableException("Failed to detect banker NPC.")

    def _get_npc_coords(self):
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

    def _talk_with_npc(self, banker_x, banker_y,):
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
            if self.is_open():
                log.info("Successfully talked with banker.")
                return
        raise RecoverableException("Failed to open banker dialogue.")

    @staticmethod
    def _load_npc_images(image_folder_path: str):
        if not os.path.exists(image_folder_path):
            raise Exception(f"Image folder path '{image_folder_path}' does not exist.")
        if not os.path.isdir(image_folder_path):
            raise Exception(f"Image folder path '{image_folder_path}' is not a directory.")
        return [load_image(image_folder_path, image) for image in os.listdir(image_folder_path)]

from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from functools import wraps
import os
from time import perf_counter

import cv2
import numpy as np
import pyautogui as pyag

from src.utilities import load_image
from src.image_detection import ImageDetection
from src.screen_capture import ScreenCapture
from src.bot.states.out_of_combat.pods_reader.reader import PodsReader
from src.bot.states.out_of_combat.status_enum import Status

from ._tabs.equipment_tab import EquipmentTab
from ._tabs.miscellaneous_tab import MiscellaneousTab
from ._tabs.resources_tab import ResourcesTab


class Vault:

    EQUIPMENT_TAB = EquipmentTab()
    MISCELLANEOUS_TAB = MiscellaneousTab()
    RESOURCES_TAB = ResourcesTab()

    @classmethod
    def deposit_all_tabs(cls):
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
                return Status.FAILED_TO_DEPOSIT_ALL_TABS
        log.info("Successfully deposited all tabs.")
        return Status.SUCCESSFULLY_DEPOSITED_ALL_TABS

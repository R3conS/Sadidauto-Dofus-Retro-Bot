from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import time
import os

import cv2
import pyautogui as pyag

# from .bank import Bank
import window_capture as wc
from src.map_changer.map_changer import MapChanger


class Banker:

    no_recall_maps = [
        "4,-16",
        "4,-17",
        "4,-18",
        "4,-19"
    ]

    def __init__(self, set_sub_state_callback):
        self.__set_sub_state_callback = set_sub_state_callback
        self.__npc_images = self.__load_npc_images()

    def __load_npc_images(self):
        image_folder_path = "src\\state\\out_of_combat\\sub_state\\banking\\images\\astrub_banker_npc"
        loaded_images = []
        for image in os.listdir(image_folder_path):
            loaded_images.append(cv2.imread(os.path.join(image_folder_path, image), cv2.IMREAD_UNCHANGED))
        return loaded_images


    def bank(self):
    
        
        while True:
            if not self.__recall_potion_used and self.map_coords == "4,-19":
                self.__recall_potion_used = True
                self.__state = BotState.CONTROLLER
                return self.__state

            elif not self.__recall_potion_used:
                if self.has_recall_potion():
                    if self.recall():
                        log.info("Successfully recalled during banking state!")
                    else:
                        log.error("Failed to recall during banking state!")
                self.__recall_potion_used = True
                self.__state = BotState.CONTROLLER
                return self.__state

            elif self.map_coords == "4,-16":
                if self.__astrub_bank():
                    self.__recall_potion_used = False
                    self.__controller.set_overloaded(False)
                    self.__state = BotState.CONTROLLER
                    return self.__state

            else:
                self.__state = BotState.MOVING
                return self.__state

    @staticmethod
    def is_char_on_no_recall_map():
        return MapChanger.get_current_map_coords() in ["4,-16", "4,-17", "4,-18", "4,-19"]

    @staticmethod
    def does_char_have_recall_potion():
        return pyag.pixelMatchesColor(664, 725, (120, 151, 154), tolerance=20)

    @staticmethod
    def use_recall_potion():
        log.info("Using 'Recall Potion' ... ")
        pyag.moveTo(664, 725)
        pyag.click(clicks=2, interval=0.1)

    @staticmethod
    def is_char_on_zaap_map():
        return MapChanger.get_current_map_coords() == "4,-19"

    def __astrub_bank(self):
        """
        'Astrub Bank' banking logic.
        
        - Close any pop-ups & interfaces.
        - Detect if inside or outside Astrub bank.
            - If not inside:
                - Move character inside.
            - Elif inside and items have been deposited:
                - Move character outside.
            - Elif inside ant items have not been deposited:
                - Open bank, deposit, close bank and return `True`.

        Program will exit if: 
        - `attempts_total` < `attempts_allowed`.
        - `timeout` seconds reached.
        
        """
        attempts_total = 0
        attempts_allowed = 5
        items_deposited = False

        while attempts_total < attempts_allowed:

            character_inside_bank = bank.Bank.inside_or_outside()

            if not character_inside_bank:
                if bank.Bank.enter_bank():
                    continue
                else:
                    attempts_total += 1

            elif character_inside_bank and items_deposited:
                if bank.Bank.exit_bank():
                    return True
                else:
                    attempts_total += 1
                    continue
                
            elif character_inside_bank and not items_deposited:

                start_time = time.time()
                timeout = 60

                while time.time() - start_time < timeout:
                    if bank.Bank.open_bank_vault():
                        if bank.Bank.deposit_items():
                            if bank.Bank.close_bank_vault():
                                items_deposited = True
                                break

                else:
                    log.critical("Failed to complete actions inside "
                                 f"bank in {timeout} seconds!")
                    log.critical("Timed out!")
                    log.critical("Exiting ... ")
                    wc.WindowCapture.on_exit_capture()

        else:
            log.critical("Failed to enter/exit bank in "
                         f"{attempts_allowed} attempts!")
            log.critical("Exiting ... ")
            wc.WindowCapture.on_exit_capture()

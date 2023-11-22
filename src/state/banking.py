from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import time

import pyautogui as pyag

from .botstate_enum import BotState
import bank
from pop_up import PopUp
import state
import data
import window_capture as wc


class Banking:

    map_coords = None
    data_map = None

    __state = None
    __recall_potion_used = False

    def __init__(self, controller):
        self.__controller = controller
        bank.Bank.img_path = data.images.npc.AstrubBanker.img_path
        bank.Bank.img_list = data.images.npc.AstrubBanker.img_list

    def banking(self):
        """
        Banking logic.

        Logic
        ----------
        - If 'Recall Potion' wasn't used:
            - Use it.
        - Elif character on "4,-16" map:
            - Launch 'Astrub Bank' banking logic.
        - Else:
            - Change 'BotState' to 'MOVING'.

        """

        while True:

            if not self.__recall_potion_used and self.map_coords == "4,-19":
                self.__recall_potion_used = True
                self.__state = BotState.CONTROLLER
                return self.__state

            elif not self.__recall_potion_used:
                if self.recall_potion_available():
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

    def recall(self):
        """
        Recall by using 'Recall Potion'.
        
        Make sure that an appropriate Zaap is saved on character. 
        For example, when using 'Astrub Forest' script, Astrub's Zaap 
        should be saved.

        """
        use_time = time.time()
        timeout = 10

        while time.time() - use_time < timeout:

            PopUp.deal()

            if self.__use_recall_potion():
                log.info("Successfully recalled to save point!")
                self.__controller.set_was_map_changed(True)
                return True
            else:
                continue

        else:
            log.error(f"Timed out in 'recall()!")
            return False

    @staticmethod
    def recall_potion_available():
        """
        Check if 'Recall Potion' is available or not.
        
        Make sure the potion is in first slot of second 'Item' row.

        """
        log.info("Checking if 'Recall Potion' is available ... ")

        color = (120, 151, 154)
        px = pyag.pixelMatchesColor(664, 725, color, tolerance=20)

        if px:
            log.info("'Recall Potion' is available!")
            return True
        else:
            log.info("'Recall Potion' is not available!")
            return False

    def __use_recall_potion(self):
        """
        Double click 'Recall Potion' in 'Items' bar.
        
        Make sure the potion is in first slot of second 'Items' row.

        """
        log.info("Using 'Recall Potion' ... ")

        pyag.moveTo(664, 725, duration=0.15)
        pyag.click(clicks=2, interval=0.1)

        if self.__controller.moving.loading_screen(3):
            log.info("Successfully used 'Recall Potion'!")
            return True

        else:
            coords = self.__controller.moving.get_coordinates(self.data_map)

            if coords == "4,-19":
                log.info("Successfully used 'Recall Potion'!")
                return True

            else:
                log.error(f"Failed to use 'Recall Potion'!")
                return False

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

            PopUp.deal()
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
                    PopUp.deal()
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

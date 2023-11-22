"""Logic related to 'BANKING' bot state."""

from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import time

import pyautogui as pyag

from .botstate_enum import BotState
import bank
from pop_up import PopUp
import state
import window_capture as wc


class Banking:
    """Holds various 'BANKING' state methods."""

    # Public class attributes.
    map_coords = None
    data_map = None

    # Private class attributes.
    __state = None
    __recall_potion_used = False

    @classmethod
    def banking(cls):
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

            if not cls.__recall_potion_used and cls.map_coords == "4,-19":
                cls.__recall_potion_used = True
                cls.__state = BotState.CONTROLLER
                return cls.__state

            elif not cls.__recall_potion_used:
                if cls.recall_potion_available():
                    if cls.recall():
                        log.info("Successfully recalled during banking state!")
                    else:
                        log.error("Failed to recall during banking state!")
                cls.__recall_potion_used = True
                cls.__state = BotState.CONTROLLER
                return cls.__state

            elif cls.map_coords == "4,-16":
                if cls.__astrub_bank():
                    cls.__recall_potion_used = False
                    cls.__state = BotState.CONTROLLER
                    return cls.__state

            else:
                cls.__state = BotState.MOVING
                return cls.__state

    @classmethod
    def recall(cls):
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

            if cls.__use_recall_potion():
                log.info("Successfully recalled to save point!")
                state.Controller.map_changed = True
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

    @classmethod
    def __use_recall_potion(cls):
        """
        Double click 'Recall Potion' in 'Items' bar.
        
        Make sure the potion is in first slot of second 'Items' row.

        """
        log.info("Using 'Recall Potion' ... ")

        pyag.moveTo(664, 725, duration=0.15)
        pyag.click(clicks=2, interval=0.1)

        if state.Moving.loading_screen(3):
            log.info("Successfully used 'Recall Potion'!")
            return True

        else:
            coords = state.Moving.get_coordinates(cls.data_map)

            if coords == "4,-19":
                log.info("Successfully used 'Recall Potion'!")
                return True

            else:
                log.error(f"Failed to use 'Recall Potion'!")
                return False

    @classmethod
    def __astrub_bank(cls):
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
                    state.Controller.fight_counter = 0
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

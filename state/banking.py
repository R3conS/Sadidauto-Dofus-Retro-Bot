"""Logic related to 'BANKING' bot state."""

from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True)

import time

from .botstate_enum import BotState
import bank
import pop_up as pu
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

            if not cls.__recall_potion_used:
                if bank.Bank.recall_potion() == "available":
                    cls.use_recall_potion()
                    cls.__recall_potion_used = True
                else:
                    cls.__recall_potion_used = True

            elif cls.map_coords == "4,-16":
                if cls.__astrub_bank():
                    cls.__recall_potion_used = False
                    cls.__state = BotState.CONTROLLER
                    return cls.__state

            else:
                cls.__state = BotState.MOVING
                return cls.__state

    @classmethod
    def use_recall_potion(cls):
        """
        Use 'Recall Potion'.
        
        Make sure that an appropriate Zaap is saved on character. 
        For example, when using 'Astrub Forest' script, Astrub's Zaap 
        should be saved.

        """
        use_time = time.time()
        timeout = 15

        while time.time() - use_time < timeout:

            pu.PopUp.deal()
            bank.Bank.use_recall_potion()
            cls.map_coords = state.Moving.get_coordinates(cls.data_map)

            if cls.map_coords == "4,-19":
                log.info("Successfully used 'Recall Potion'!")
                return True

        else:
            log.error(f"Failed to use 'Recall Potion' in {timeout} seconds!")
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

            pu.PopUp.deal()
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
                    pu.PopUp.deal()
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

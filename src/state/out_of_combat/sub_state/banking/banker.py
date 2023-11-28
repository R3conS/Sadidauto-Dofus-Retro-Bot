from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import os


from .handlers.not_on_bank_map import Handler as Handler_NotOnBankMap
from .handlers.on_bank_map import Handler as Handler_OnBankMap
from ._status_codes_enum import Status
from src.map_changer.map_changer import MapChanger


class Banker:

    def __init__(
            self, 
            set_sub_state_callback: callable, 
            script: str, 
            game_window_title: str
        ):
        self.__set_sub_state_callback = set_sub_state_callback
        self.__script = script
        self.__game_window_title = game_window_title

    def bank(self):
        if not self.is_char_on_astrub_bank_map():
            status = Handler_NotOnBankMap(self.__script).handle()
            if status == Status.FAILED_TO_RECALL:
                log.critical("Not implemented!")
                # ToDo: link to recovery state.
                os._exit(1)

        if self.is_char_on_astrub_bank_map():
            status = Handler_OnBankMap(self.__game_window_title).handle()
            if (
                status == Status.FAILED_TO_ENTER_BANK
                or status == Status.FAILED_TO_OPEN_BANK_VAULT
                or status == Status.FAILED_TO_DEPOSIT_ALL_TABS
                or status == Status.FAILED_TO_CLOSE_BANK_VAULT
                or status == Status.FAILED_TO_LEAVE_BANK
            ):
                log.critical("Not implemented!")
                # ToDo: link to recovery state.
                os._exit(1)
        
        log.info("Finished banking.")
        os._exit(1)

    @classmethod
    def is_char_on_astrub_bank_map(cls):
        return MapChanger.get_current_map_coords() == "4,-16"

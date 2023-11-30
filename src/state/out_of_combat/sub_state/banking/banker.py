from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from .handlers.not_on_bank_map import Handler as Handler_NotOnBankMap
from .handlers.on_bank_map import Handler as Handler_OnBankMap
from .status_enum import Status
from src.map_changer.map_changer import MapChanger


class Banker:

    def __init__(self, script: str, game_window_title: str):
        self.__script = script
        self.__game_window_title = game_window_title

    def bank(self):
        if not self.is_char_on_astrub_bank_map():
            status = Handler_NotOnBankMap(self.__script).handle()
            if status == Status.FAILED_TO_RECALL:
                return Status.FAILED_TO_FINISH_BANKING

        if self.is_char_on_astrub_bank_map():
            status = Handler_OnBankMap(self.__game_window_title).handle()
            if (
                status == Status.FAILED_TO_ENTER_BANK
                or status == Status.FAILED_TO_OPEN_BANK_VAULT
                or status == Status.FAILED_TO_DEPOSIT_ALL_TABS
                or status == Status.FAILED_TO_CLOSE_BANK_VAULT
                or status == Status.FAILED_TO_LEAVE_BANK
            ):
                return Status.FAILED_TO_FINISH_BANKING
        
        log.info("Successfully finished banking!")
        return Status.SUCCESSFULLY_FINISHED_BANKING

    @classmethod
    def is_char_on_astrub_bank_map(cls):
        return MapChanger.get_current_map_coords() == "4,-16"

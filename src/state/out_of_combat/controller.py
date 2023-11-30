from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from src.interfaces import Interfaces
from .pods_reader.pods_reader import PodsReader
from src.state.botstate_enum import BotState
from .sub_state.hunting.hunter import Hunter
from .sub_state.banking.banker import Banker
from .sub_state.banking.status_enum import Status as BankerStatus
from .sub_state.hunting.status_enum import Status as HunterStatus


class Controller:
    
    __pod_limit = 10

    def __init__(
            self, 
            set_bot_state_callback: callable, 
            script: str,
            game_window_title: str,
            game_window_size: tuple[int, int]
        ):
        self.__set_bot_state_callback = set_bot_state_callback
        self.__hunter = Hunter(script, game_window_title, game_window_size)
        self.__banker = Banker(script, game_window_title)

    def run(self):
        while True:
            sub_state = self.__determine_sub_state()
            
            if sub_state == _SubState.HUNTING:
                status = self.__hunter.hunt()
                if status == HunterStatus.SUCCESSFULLY_FINISHED_HUNTING:
                    continue
                elif status == HunterStatus.FAILED_TO_FINISH_HUNTING:
                    log.info(f"Failed to finish hunting. Attempting to recover ...")
                    self.__set_bot_state_callback(BotState.RECOVERY)
                    return

            elif sub_state == _SubState.BANKING:
                status = self.__banker.bank()
                if status == BankerStatus.SUCCESSFULLY_FINISHED_BANKING:
                    continue
                elif status == BankerStatus.FAILED_TO_FINISH_BANKING:
                    log.info(f"Failed to finish banking. Attempting to recover ...")
                    self.__set_bot_state_callback(BotState.RECOVERY)
                    return
                
            elif sub_state == _SubState.RECOVERY:
                log.info("'Out of Combat' controller failed to determine its sub state. Attempting to recover ...")
                self.__set_bot_state_callback(BotState.RECOVERY)
                return

    def __determine_sub_state(self):
        pods_percentage = self.__get_pods_percentage()
        if pods_percentage is not None:
            if pods_percentage >= self.__pod_limit:
                log.info(f"Reached pods limit of: {self.__pod_limit}%. Going to bank ... ")
                return _SubState.BANKING
            log.info(f"Not at pods limit. Hunting ...")
            return _SubState.HUNTING
        log.info("'Out of Combat' controller failed to determine its sub state.")
        return _SubState.RECOVERY

    def __get_pods_percentage(self):
        log.info("Getting inventory pods percentage ... ")
        Interfaces.open_inventory()
        if Interfaces.is_inventory_open():
            percentage = PodsReader.get_occupied_inventory_percentage()
            if percentage is not None:
                log.info(f"Inventory is {percentage}% full.")
                Interfaces.close_inventory()
                if not Interfaces.is_inventory_open():
                    return percentage
            else:
                log.info("Failed to get inventory pods percentage.")
                PodsReader.save_images_for_debug()
        return None


class _SubState:

    HUNTING = "HUNTING"
    BANKING = "BANKING"
    RECOVERY = "RECOVERY"

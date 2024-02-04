from src.logger import Logger
log = Logger.get_logger()

from time import perf_counter

import pyautogui as pyag

from src.bot._exceptions import ExceptionReason, RecoverableException, UnrecoverableException
from src.bot._interfaces.interfaces import Interfaces
from src.bot._map_changer.map_changer import MapChanger
from src.bot._recoverer._reconnecter.reconnecter import Reconnecter
from src.bot._states.in_combat._sub_states.sub_states_enum import State as InCombat_SubState
from src.bot._states.state_determiner.determiner import determine_state
from src.bot._states.states_enum import State


class Recoverer:

    def __init__(
            self, 
            character_name: str, 
            server_name: str, 
            character_level: int,
            game_window_identifier: int | str, # String (title) only used for dev/testing.
            game_window_default_size: tuple[int, int]
        ):
        self._character_name = character_name
        self._server_name = server_name
        self._character_level = character_level
        self._game_window_default_size = game_window_default_size
        self._exception_tracker = {}
        self._max_consecutive_exceptions = 3
        self._max_consecutive_exceptions_period = 120 # Seconds.
        self._reconnecter = Reconnecter(
            character_name, 
            server_name, 
            character_level, 
            game_window_identifier, 
            game_window_default_size
        )

    def recover(
            self, 
            exception_reason: ExceptionReason, 
            exception_occured_in_sub_state: InCombat_SubState = None
        ):
        """
        Attempt to recover from an exception.

        - Will raise `UnrecoverableException` if the same exception has occured
        in the main BOT loop more than `max_consecutive_exceptions` times in a row
        within `max_consecutive_exceptions_period` seconds.
        - Will raise `UnrecoverableException` if the bot cannot recover in 
        `max_attempts` attempts when attempting to recover from an exception 
        raised in the main BOT loop.
        """
        self._check_exception_consecutiveness(exception_reason)

        max_attempts = 3
        total_attempts = 0
        while total_attempts < max_attempts:
            log.info("Attempting to recover ... ")
            try:
                self._manage_exception(exception_reason, exception_occured_in_sub_state)
            except RecoverableException as e:
                total_attempts += 1
                exception_reason = e.reason
                log.error(f"Failed to recover! ({total_attempts}/{max_attempts})")
                continue
            log.info("Successfully recovered!")
            break
        else:
            raise UnrecoverableException(f"Failed to recover in '{max_attempts}' attempts.")

    def _check_exception_consecutiveness(self, reason: ExceptionReason):
        """
        Check if the same exception has occured a specified number of times
        within a specified period of time. When this happens it means
        that the bot can't recover from the exception.
        """
        if reason not in self._exception_tracker:
            self._exception_tracker = {}

        current_time = perf_counter()
        if reason in self._exception_tracker:
            if (
                self._exception_tracker[reason]["count"] >= self._max_consecutive_exceptions
                and current_time - self._exception_tracker[reason]["timestamp"] <= self._max_consecutive_exceptions_period
            ):
                raise UnrecoverableException(
                    f"Same exception '{reason}' "
                    f"occurred '{self._max_consecutive_exceptions}' times in a row "
                    f"within '{self._max_consecutive_exceptions_period}' seconds."
                )
            else:
                self._exception_tracker[reason]["count"] += 1
                self._exception_tracker[reason]["timestamp"] = current_time
        else:
            self._exception_tracker[reason] = {"count": 1, "timestamp": current_time}
        
        log.info(f"Exception '{reason}' occurred '{self._exception_tracker[reason]['count']}' times in a row.")
    
    def _manage_exception(
            self, 
            reason: ExceptionReason, 
            occured_in_sub_state: InCombat_SubState = None
        ):
        if reason == ExceptionReason.UNSPECIFIED:
            if not self._reconnecter._is_account_connected():
                self._reconnecter.reconnect(occured_in_sub_state)
            else:
                Interfaces.close_all()
        elif reason == ExceptionReason.FAILED_TO_CHANGE_MAP:
            if not self._reconnecter._is_account_connected():
                self._reconnecter.reconnect(occured_in_sub_state)
            elif determine_state() == State.OUT_OF_COMBAT:
                Interfaces.close_all()
                self._emergency_recall()
        elif reason == ExceptionReason.FAILED_TO_GET_MAP_COORDS:
            if not self._reconnecter._is_account_connected():
                self._reconnecter.reconnect(occured_in_sub_state)
            else:
                Interfaces.close_all()

    @classmethod
    def _emergency_recall(cls):
        log.info("Attempting to recall ... ")
        if cls._is_recall_potion_available():
            pyag.moveTo(664, 725)
            pyag.click(clicks=2, interval=0.1)
            try:
                MapChanger.wait_loading_screen_pass()
            except RecoverableException as e:
                e.exception_reason = ExceptionReason.FAILED_TO_CHANGE_MAP
                raise e
            log.info("Successfully recalled.")
            return
        raise UnrecoverableException("Recall potion is not available.")
            
    @staticmethod
    def _is_recall_potion_available():
        return pyag.pixelMatchesColor(664, 725, (120, 151, 154), tolerance=20)


if __name__ == "__main__":
    recoverer = Recoverer("Juni", "Semi-like", 65, "Abrak", (950, 785))

from src.logger import Logger
log = Logger.get_logger(Logger.DEBUG, True, True)

from time import perf_counter

import pyautogui as pyag

from src.bot._exceptions import ExceptionReason, UnrecoverableException
from src.bot._interfaces.interfaces import Interfaces
from src.bot._map_changer.map_changer import MapChanger
from src.bot._recoverer._reconnecter.reconnecter import Reconnecter


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

    def recover(self, exception_reason: ExceptionReason):
        if not isinstance(exception_reason, ExceptionReason):
            raise ValueError(f"Invalid 'exception_reason' type: {type(exception_reason)}.")
        log.info(f"Attempting to recover ... ")
        self._check_exception_consecutiveness(exception_reason)
        self._manage_exception(exception_reason)
        log.info(f"Successfully recovered.")

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
                    f"occurred over '{self._max_consecutive_exceptions}' times in a row "
                    f"within '{self._max_consecutive_exceptions_period}' seconds."
                )
            else:
                self._exception_tracker[reason]["count"] += 1
                self._exception_tracker[reason]["timestamp"] = current_time
        else:
            self._exception_tracker[reason] = {"count": 1, "timestamp": current_time}

    def _manage_exception(self, reason: ExceptionReason):
        if reason == ExceptionReason.UNSPECIFIED:
            if self._is_disconnected():
                self._reconnecter.reconnect()
                return
            Interfaces.close_all()
        elif reason == ExceptionReason.FAILED_TO_GET_MAP_COORDS:
            if self._is_disconnected():
                self._reconnecter.reconnect()
                return
            raise UnrecoverableException("Failed to get map coords because the map image is missing.")
        elif reason == ExceptionReason.FAILED_TO_WAIT_FOR_LOADING_SCREEN_DURING_MAP_CHANGE:
            if self._is_disconnected():
                self._reconnecter.reconnect()
            Interfaces.close_all()
            self._emergency_recall()

    @staticmethod
    def _is_disconnected():
        """If chat, minimap, spell/item bar, interface icons etc. are not visible."""
        return not (
            pyag.pixelMatchesColor(673, 747, (213, 207, 170))
            # Color is different when an offer (exchange, group invite, etc.) is on screen.
            or pyag.pixelMatchesColor(673, 747, (192, 186, 153))
        )

    @classmethod
    def _emergency_recall(cls):
        log.info("Attempting to recall ... ")
        if cls._is_recall_potion_available():
            pyag.moveTo(664, 725)
            pyag.click(clicks=2, interval=0.1)
            MapChanger.wait_loading_screen_pass()
            log.info("Successfully recalled.")
            return
        raise UnrecoverableException("Recall potion is not available.")
            
    @staticmethod
    def _is_recall_potion_available():
        return pyag.pixelMatchesColor(664, 725, (120, 151, 154), tolerance=20)


if __name__ == "__main__":
    recoverer = Recoverer("Juni", "Semi-like", 65, "Abrak", (950, 785))
    recoverer.recover(ExceptionReason.UNSPECIFIED)

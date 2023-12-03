from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from ._turn_bar import TurnBar
from ._tactical_mode import TacticalMode
from ._models import Models
from ..status_enum import Status


class Handler:
    """Handle turn bar, tactical mode and models."""

    @staticmethod
    def handle():
        log.info("Handling fight preferences ... ")

        log.info("Handling turn bar ... ")
        if not TurnBar.is_shrunk():
            log.info("Turn bar is not shrunk. Shrinking it ... ")
            result = TurnBar.shrink()
            if result == Status.TIMED_OUT_WHILE_SHRINKING_TURN_BAR:
                return result
        else:
            log.info("Turn bar is already shrunk.")
            
        log.info("Handling tactical mode ... ")
        if not TacticalMode.is_on():
            log.info("Tactical mode is off. Turning it on ... ")
            result = TacticalMode.turn_on()
            if (
                result == Status.FAILED_TO_GET_TACTICAL_MODE_TOGGLE_ICON_POS
                or result == Status.TIMED_OUT_WHILE_TURNING_ON_TACTICAL_MODE
            ):
                return result
        else:
            log.info("Tactical mode is already on.")

        log.info("Handling models ... ")
        if Models.is_toggle_icon_visible():
            if not Models.are_disabled():
                log.info("Models are not disabled. Disabling them ... ")
                result = Models.disable()
                if (
                    result == Status.FAILED_TO_GET_MODELS_TOGGLE_ICON_POS
                    or result == Status.TIMED_OUT_WHILE_DISABLING_MODELS
                ):
                    return result
            else:
                log.info("Models are already disabled.")
        else:
            log.info("Models toggle icon is not visible.")
            return Status.MODELS_TOGGLE_ICON_NOT_VISIBLE
        
        return Status.SUCCESSFULLY_HANDLED_FIGHT_PREFERENCES

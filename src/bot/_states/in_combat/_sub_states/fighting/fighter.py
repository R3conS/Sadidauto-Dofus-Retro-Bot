from src.logger import get_logger

log = get_logger()

from src.bot._exceptions import RecoverableException
from src.bot._interfaces.interfaces import Interfaces
from src.bot._states.in_combat._status_enum import Status
from src.bot._states.in_combat._sub_states.fighting._first_turn_handler.handler import Handler as FirstTurnHandler
from src.bot._states.in_combat._sub_states.fighting._subsequent_turn_handler.handler import Handler as SubsequentTurnHandler
from src.bot._states.in_combat._sub_states.fighting._turn_detector import TurnDetector
from src.bot._states.in_combat._sub_states.sub_states_enum import State as SubState


class Fighter:

    def __init__(self, script: str, character_name: str):
        self._script = script
        self._character_name = character_name

    def fight(self):
        try:
            while True:
                if TurnDetector.detect_start_of_turn(self._character_name) == Status.FIGHT_RESULTS_WINDOW_DETECTED:
                    Interfaces.FIGHT_RESULTS.close()
                    return
                else:
                    if TurnDetector.is_first_turn():
                        FirstTurnHandler.handle(self._script, self._character_name)
                    else:
                        SubsequentTurnHandler.handle(self._character_name)
                    TurnDetector.pass_turn(self._character_name)
        except RecoverableException as e:
            e.occured_in_sub_state = SubState.FIGHTING
            raise e

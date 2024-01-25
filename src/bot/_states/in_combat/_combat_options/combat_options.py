from src.bot._states.in_combat._combat_options._fight_lock import FightLock
from src.bot._states.in_combat._combat_options._models import Models
from src.bot._states.in_combat._combat_options._tactical_mode import TacticalMode
from src.bot._states.in_combat._combat_options._turn_bar import TurnBar


class CombatOptions:

    FIGHT_LOCK = FightLock()
    MODELS = Models()
    TACTICAL_MODE = TacticalMode()
    TURN_BAR = TurnBar()

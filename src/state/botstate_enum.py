from enum import Enum


class BotState(Enum):

    OUT_OF_COMBAT = "OUT_OF_COMBAT"
    IN_COMBAT = "IN_COMBAT"
    RECOVERY = "RECOVERY"
    
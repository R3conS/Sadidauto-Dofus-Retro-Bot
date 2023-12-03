from enum import Enum


class Status(Enum):

    SUCCESSFULLY_DETECTED_TURN = "successfully_detected_turn"
    TIMED_OUT_WHILE_DETECTING_TURN = "timed_out_while_detecting_turn"

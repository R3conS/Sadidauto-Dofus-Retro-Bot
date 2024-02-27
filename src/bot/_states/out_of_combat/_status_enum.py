from enum import Enum


class Status(Enum):

    SUCCESSFULLY_ATTACKED_MONSTER = "successfully_attacked_monster"
    SUCCESSFULLY_TRAVERSED_MAP = "successfully_traversed_map"
    MAP_FULLY_SEARCHED = "map_fully_searched"
    REACHED_PODS_LIMIT = "reached_pods_limit"
    FAILED_TO_ATTACK_MONSTER = "failed_to_attack_monster"
    MONSTER_IS_ALREADY_IN_COMBAT = "monster_is_already_in_combat"

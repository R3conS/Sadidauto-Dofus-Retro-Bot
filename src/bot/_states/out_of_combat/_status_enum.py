from enum import Enum


class Status(Enum):

    SUCCESSFULLY_ATTACKED_MONSTER = "successfully_attacked_monster"
    SUCCESSFULLY_TRAVERSED_MAP = "successfully_traversed_map"
    MAP_FULLY_SEARCHED = "map_fully_searched"
    REACHED_PODS_LIMIT = "reached_pods_limit"
    TIMED_OUT_WHILE_ATTACKING_MONSTER = "failed_to_attack_monster"
    MONSTER_IS_ALREADY_IN_COMBAT = "monster_is_already_in_combat"
    MONSTER_IS_NO_LONGER_AT_LOCATION = "monster_is_no_longer_at_location"
    MAP_WAS_CHANGED_BY_ACCIDENT = "map_was_changed_by_accident"
    ENTERED_LUMBERJACKS_WORKSHOP_BY_ACCIDENT = "entered_lumberjacks_worksop_by_accident"
    MONSTER_MOVED_FROM_INITIAL_LOCATION = "monster_moved_from_initial_location"
    ATTACK_TOOLTIP_NOT_FOUND = "attack_tooltip_not_found"

from enum import Enum


class Status(Enum):
    

    SUCCESSFULLY_TRAVERSED_MAP = "successfully_traversed_map"
    SUCCESSFULLY_STARTED_COMBAT = "successfully_started_combat"
    SUCCESSFULLY_FINISHED_HUNTING = "successfully_finished_hunting"

    FAILED_TO_TRAVERSE_MAP = "failed_to_traverse_map"
    FAILED_TO_LEAVE_LUMBERJACK_WORKSHOP = "failed_to_leave_lumberjack_workshop"
    FAILED_TO_CHANGE_MAP = "failed_to_change_map"
    FAILED_TO_FINISH_HUNTING = "failed_to_finish_hunting"
    FAILED_TO_CHANGE_MAP_BACK_TO_ORIGINAL = "failed_to_change_map_back_to_original"

    MAP_FULLY_SEARCHED = "map_fully_searched"
    REACHED_PODS_LIMIT = "reached_pods_limit"

from random import choice as random_choice

from src.bot._states.out_of_combat._sub_states.hunting._monster_tooltip_finder.tooltip import Tooltip


class Sorter:

    MONSTERS = ["Boar", "Mush Mush", "Prespic", "Moskito", "Miliboowolf"]
    SORT_BY_MONSTER_PRIORITY = 1
    SORT_BY_MONSTER_GROUP_SCORE = 2
    SORT_BY_MONSTER_AMOUNT = 3
    SORT_BY_TOOLTIP_RECTANGLE_AREA = 4

    @classmethod
    def sort(cls, tooltips: list[Tooltip], sort_by: int = SORT_BY_MONSTER_PRIORITY):
        """
        Sorts the tooltips based on the given criteria. Always from highest to lowest.
        """
        if sort_by in (cls.SORT_BY_MONSTER_PRIORITY, cls.SORT_BY_MONSTER_GROUP_SCORE, cls.SORT_BY_MONSTER_AMOUNT):
            tooltips = {tooltip: tooltip.monster_counts for tooltip in tooltips}
            if sort_by == cls.SORT_BY_MONSTER_PRIORITY:
                return cls._sort_by_monster_priority(tooltips)
            elif sort_by == cls.SORT_BY_MONSTER_GROUP_SCORE:
                return cls._sort_by_monster_group_score(tooltips)
            elif sort_by == cls.SORT_BY_MONSTER_AMOUNT:
                return cls._sort_by_monster_amount(tooltips)
        elif sort_by == cls.SORT_BY_TOOLTIP_RECTANGLE_AREA:
            return cls._sort_by_rectangle_area({tooltip: tooltip.rectangle_area for tooltip in tooltips})
        else:
            raise ValueError(f"Invalid value for 'sort_by': '{sort_by}'.")

    @classmethod
    def _sort_by_monster_priority(cls, tooltips: dict):
        """
        Sorts the tooltips by the priority of the monsters.

        The lower the element index of a monster in the `cls.MONSTERS` list,
        the higher its priority.
        """
        sorted_tooltips = []
        for _ in range(len(tooltips)):
            key = cls._get_tooltip_with_most_priority_monsters(tooltips)
            sorted_tooltips.append(key)
            tooltips.pop(key)
        return sorted_tooltips
    
    @classmethod
    def _sort_by_monster_group_score(cls, tooltips: dict):
        """
        Sorts the tooltips by the score value of the monster group.

        The lower the element index of a monster in the `cls.MONSTERS` list, 
        the higher its score value.
        """
        tooltips_with_scores = {}
        for key, monster_counts in tooltips.items():
            score = 0
            for i, monster_name in enumerate(cls.MONSTERS):
                score += monster_counts.get(monster_name, 0) * (len(cls.MONSTERS) - i)
            tooltips_with_scores[key] = score
        return sorted(tooltips_with_scores, key=tooltips_with_scores.get, reverse=True)

    @staticmethod
    def _sort_by_monster_amount(tooltips: dict):
        """Sort by the amount of monsters in the group."""
        tooltips = {key: sum(monster_counts.values()) for key, monster_counts in tooltips.items()}
        return sorted(tooltips, key=tooltips.get, reverse=True)

    @staticmethod
    def _sort_by_rectangle_area(tooltips: dict):
        return sorted(tooltips, key=tooltips.get, reverse=True)

    @staticmethod
    def _get_tooltips_with_highest_monster_count(tooltips: dict, monster_name: str):
        highest_monster_count = 0
        highest_monster_count_tooltips_keys = []

        for key, tooltip_monsters in tooltips.items():
            if tooltip_monsters.get(monster_name, 0) > highest_monster_count:
                highest_monster_count = tooltip_monsters.get(monster_name, 0)
                highest_monster_count_tooltips_keys = [key]
            elif tooltip_monsters.get(monster_name, 0) == highest_monster_count:
                highest_monster_count_tooltips_keys.append(key)

        return highest_monster_count_tooltips_keys

    @classmethod
    def _get_tooltip_with_most_priority_monsters(cls, tooltips: dict):
        for monster_name in cls.MONSTERS:
            keys = cls._get_tooltips_with_highest_monster_count(tooltips, monster_name)
            if len(keys) == 1:
                return keys[0]
            tooltips = {key: tooltips[key] for key in keys}
        return random_choice(keys)


if __name__ == "__main__":
    tooltips_dict = { # tooltip: monster_counts
        0: {"Boar": 1, "Mush Mush": 55, "Prespic": 1},
        1: {"Boar": 1, "Mush Mush": 1, "Prespic": 1},
        2: {"Boar": 1, "Mush Mush": 15, "Prespic": 1},
        3: {"Boar": 1, "Mush Mush": 1, "Prespic": 1, "Moskito": 25, "Miliboowolf": 1},
        4: {"Boar": 1, "Mush Mush": 1, "Prespic": 1, "Moskito": 1, "Miliboowolf": 25},
    }

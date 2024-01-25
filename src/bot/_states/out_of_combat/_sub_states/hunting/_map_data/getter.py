from src.bot._states.out_of_combat._sub_states.hunting._map_data._af_anticlock import Anticlock
from src.bot._states.out_of_combat._sub_states.hunting._map_data._af_clockwise import Clockwise


class Getter:
    
    @staticmethod
    def get_data_object(script: str):
        if script == "af_anticlock":
            return Anticlock
        elif script == "af_clockwise":
            return Clockwise
        else:
            raise ValueError(f"No hunting data for script: {script}")

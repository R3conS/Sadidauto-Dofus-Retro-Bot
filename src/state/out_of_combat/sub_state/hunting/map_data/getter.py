from ._anticlock import AntiClock


class Getter:
    
    @staticmethod
    def get_data_object(script: str):
        if script == "af_anticlock":
            return AntiClock
        else:
            raise ValueError(f"No hunting data for script: {script}")

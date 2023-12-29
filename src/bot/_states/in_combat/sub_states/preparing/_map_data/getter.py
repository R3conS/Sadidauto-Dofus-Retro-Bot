from ._astrub_forest import AstrubForest


class Getter:
    
    @staticmethod
    def get_data_object(script: str):
        if script == "af_anticlock" or script == "af_clockwise":
            return AstrubForest
        else:
            raise ValueError(f"No cell data for script: {script}")

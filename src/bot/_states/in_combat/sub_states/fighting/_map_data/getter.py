from ._astrub_forest import AstrubForest


class Getter:
    
    @staticmethod
    def get_data_object(script: str):
        if script.startswith("af_"):
            return AstrubForest
        else:
            raise ValueError(f"No fighting data for script: {script}")

from ._astrub_bank import AstrubBank


class Getter:
    
    @staticmethod
    def get_data_object(script: str):
        if script.startswith("af_"):
            return AstrubBank
        else:
            raise ValueError(f"No banking data for script: {script}")

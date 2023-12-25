class Clockwise:

    @staticmethod
    def get_pathing_data():
        return { # {from_map: to_map}
            "4,-16" : "4,-17", # 4,-16 is the Astrub Bank map
            "4,-17" : "4,-18",
            "4,-18" : "4,-19",
            "4,-19" : "4,-20",
            "4,-20" : "4,-21",
            "4,-21" : "5,-21",
            "5,-21" : "5,-22",
            "5,-22" : "5,-23",
            "5,-23" : "4,-23",
            "4,-23" : "3,-23",
            "3,-23" : "2,-23",
            "2,-23" : "1,-23", # 2,-23 is the beginning of Astrub Forest
            "1,-23" : "0,-23",
            "0,-23" : "-1,-23",
            "-1,-23": "-1,-24",
            "-1,-24": "-2,-24",
            "-2,-24": "-2,-25",
            "-2,-25": "-2,-26",
            "-2,-26": "-2,-27",
            "-2,-27": "-2,-28",
            "-2,-28": "-1,-28",
            "-1,-28": "0,-28",
            "0,-28" : "0,-27",
            "0,-27" : "0,-26",
            "0,-26" : "0,-25",
            "0,-25" : "0,-24",
            "0,-24" : "1,-24",
            "1,-24" : "1,-25",
            "1,-25" : "1,-26",
            "1,-26" : "1,-27",
            "1,-27" : "1,-28",
            "1,-28" : "2,-28",
            "2,-28" : "2,-27",
            "2,-27" : "3,-27",
            "3,-27" : "3,-26",
            "3,-26" : "2,-26",
            "2,-26" : "2,-25",
            "2,-25" : "2,-24",
            "2,-24" : "2,-23", # Back to the beginning of Astrub Forest
        }

    @staticmethod
    def get_map_type_data():
        return {
            "4,-16" : "traversable", # Astrub Bank map
            "4,-17" : "traversable",
            "4,-18" : "traversable",
            "4,-19" : "traversable",
            "4,-20" : "traversable",
            "4,-21" : "traversable",
            "5,-21" : "traversable",
            "5,-22" : "traversable",
            "5,-23" : "traversable",
            "4,-23" : "traversable",
            "3,-23" : "traversable",
            "2,-23" : "traversable",
            "2,-24" : "traversable",
            "2,-25" : "traversable",
            "2,-26" : "traversable",
            "3,-26" : "traversable",
            "3,-27" : "traversable",
            "2,-27" : "traversable",
            "2,-28" : "traversable",
            "1,-28" : "traversable",
            "1,-27" : "traversable",
            "1,-26" : "traversable",
            "1,-25" : "traversable",
            "1,-24" : "traversable",
            "0,-24" : "traversable",
            "0,-25" : "traversable",
            "0,-26" : "traversable",
            "0,-27" : "traversable",
            "0,-28" : "traversable",
            "-1,-28": "traversable",
            "-2,-28": "traversable",
            "-2,-27": "traversable",
            "-2,-26": "traversable",
            "-2,-25": "traversable",
            "-2,-24": "traversable",
            "-1,-24": "traversable",
            "-1,-23": "traversable",
            "0,-23" : "traversable",
            "1,-23" : "traversable",
        }

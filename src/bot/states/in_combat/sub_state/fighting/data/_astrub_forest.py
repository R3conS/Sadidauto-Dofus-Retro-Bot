class AstrubForest:

    @staticmethod
    def get_movement_data():
        return {
            "3,-25" : {"red" : {(234, 237): (365, 308), (267, 221): (400, 291)}, "blue": {(700, 442): (567, 375), (733, 425): (597, 358)}},
            "3,-26" : {"red" : (532, 290), "blue": (499, 374)},
            "2,-26" : {"red" : (499, 240), "blue": (531, 223)},
            "2,-28" : {"red" : (525, 358), "blue": (594, 393)},
            "1,-28" : {"red" : (260, 326), "blue": (427, 409)},
            "1,-26" : {"red" : (599, 257), "blue": (766, 342)},
            "1,-25" : {"red" : (698, 408), "blue": (665, 358)},
            "2,-25" : {"red" : (395, 225), "blue": (494, 376)},
            "2,-24" : {"red" : (527, 393), "blue": (660, 428)},
            "1,-24" : {"red" : (461, 394), "blue": (194, 257)},
            "0,-24" : {"red" : (432, 239), "blue": (499, 239)}, 
            "-2,-26": {"red" : (504, 474), "blue": (699, 341)},
            "-2,-24": {"red" : (461, 325), "blue": {(567, 305): (560, 308), (434, 373): (427, 376)}},
            "-1,-23": {"red" : (761, 445), "blue": (498, 308)},
            "1,-23" : {"red" : (394, 360), "blue": (661, 291)},
            "2,-27" : {"red" : (531, 324), "blue": (567, 340)},
            "1,-27" : {"red" : (465, 290), "blue": (299, 307)},
            "0,-25" : {"red" : (500, 341), "blue": (532, 358)},
            "0,-28" : {"red" : (531, 357), "blue": (565, 340)},
            "-2,-28": {"red" : {(400, 355): (400, 355), (534, 355): (505, 375)}, "blue": {(468, 322): (468, 322), (468, 357): (468, 357)}},
        }

    @staticmethod
    def get_spell_casting_data():
        """
        Stores the coordinates where the spells have to be cast. If
        the value of a key (spell name) is a dictionary, then the
        keys of those dictionaries are the coordinates of the starting
        cell where character started the fight.
        """
        return {
            "3,-25" : {"red" : {"earthquake": {(234, 237): (466, 359), (267, 221): (499, 342)}, "poisoned_wind": {(234, 237): (466, 359), (267, 221): (499, 342)}, "sylvan_power": {(234, 237): (365, 308), (267, 221): (400, 291)}},
                       "blue": {"earthquake": {(700, 442): (464, 325), (733, 425): (496, 306)}, "poisoned_wind": {(700, 442): (464, 325), (733, 425): (496, 306)}, "sylvan_power": {(700, 442): (567, 375), (733, 425): (597, 358)}}},
            "3,-26" : {"red" : {"earthquake": (532, 290), "poisoned_wind": (532, 290), "sylvan_power": (532, 290)},
                       "blue": {"earthquake": (599, 322), "poisoned_wind": (599, 322), "sylvan_power": (499, 374)}},
            "2,-26" : {"red" : {"earthquake": (499, 240), "poisoned_wind": (499, 240), "sylvan_power": (499, 240)},
                       "blue": {"earthquake": (531, 223), "poisoned_wind": (531, 223), "sylvan_power": (531, 223)}},
            "2,-28" : {"red" : {"earthquake": (632, 407), "poisoned_wind": (632, 407), "sylvan_power": (527, 361)},
                       "blue": {"earthquake": (498, 341), "poisoned_wind": (498, 341), "sylvan_power": (593, 393)}},
            "1,-28" : {"red" : {"earthquake": (260, 326), "poisoned_wind": (260, 326), "sylvan_power": (260, 326)},
                       "blue": {"earthquake": (427, 409), "poisoned_wind": (427, 409), "sylvan_power": (427, 409)}},
            "1,-26" : {"red" : {"earthquake": (498, 308), "poisoned_wind": (498, 308), "sylvan_power": (599, 257)},
                       "blue": {"earthquake": (667, 288), "poisoned_wind": (667, 288), "sylvan_power": (766, 341)}},
            "1,-25" : {"red" : {"earthquake": (599, 359), "poisoned_wind": (599, 359), "sylvan_power": (698, 408)},
                       "blue": {"earthquake": (665, 358), "poisoned_wind": (665, 358), "sylvan_power": (665, 358)}},
            "2,-25" : {"red" : {"earthquake": (395, 225), "poisoned_wind": (395, 225), "sylvan_power": (395, 225)},
                       "blue": {"earthquake": (399, 323), "poisoned_wind": (399, 323), "sylvan_power": (494, 376)}},
            "2,-24" : {"red" : {"earthquake": (527, 393), "poisoned_wind": (527, 393), "sylvan_power": (527, 393)},
                       "blue": {"earthquake": (660, 428), "poisoned_wind": (660, 428), "sylvan_power": (660, 428)}},
            "1,-24" : {"red" : {"earthquake": (366, 342), "poisoned_wind": (366, 342), "sylvan_power": (461, 394)},
                       "blue": {"earthquake": (299, 308), "poisoned_wind": (299, 308), "sylvan_power": (194, 257)}},
            "0,-24" : {"red" : {"earthquake": (531, 291), "poisoned_wind": (531, 291), "sylvan_power": (432, 239)},
                       "blue": {"earthquake": (399, 188), "poisoned_wind": (399, 188), "sylvan_power": (499, 239)}},
            "-2,-26": {"red" : {"earthquake": (598, 426), "poisoned_wind": (598, 426), "sylvan_power": (504, 474)},
                       "blue": {"earthquake": (599, 393), "poisoned_wind": (599, 393), "sylvan_power": (699, 341)}},
            "-2,-24": {"red" : {"earthquake": (461, 325), "poisoned_wind": (461, 325), "sylvan_power": (461, 325)},
                       "blue": {"earthquake": {(567, 305): (560, 308), (434, 373): (427, 376)}, "poisoned_wind": {(567, 305): (560, 308), (434, 373): (427, 376)}, "sylvan_power": {(567, 305): (560, 308), (434, 373): (427, 376)}}},
            "-1,-23": {"red" : {"earthquake": (761, 445), "poisoned_wind": (761, 445), "sylvan_power": (761, 445)},
                       "blue": {"earthquake": (498, 308), "poisoned_wind": (498, 308), "sylvan_power": (498, 308)}},
            "1,-23" : {"red" : {"earthquake": (394, 360), "poisoned_wind": (394, 360), "sylvan_power": (394, 360)},
                       "blue": {"earthquake": (661, 291), "poisoned_wind": (661, 291), "sylvan_power": (661, 291)}},
            "2,-27" : {"red" : {"earthquake": (432, 271), "poisoned_wind": (432, 271), "sylvan_power": (531, 324)},
                       "blue": {"earthquake": (666, 391), "poisoned_wind": (666, 391), "sylvan_power": (567, 340)}},
            "1,-27" : {"red" : {"earthquake": (366, 238), "poisoned_wind": (366, 238), "sylvan_power": (465, 290)},
                       "blue": {"earthquake": (400, 357), "poisoned_wind": (400, 357), "sylvan_power": (299, 307)}},
            "0,-25" : {"red" : {"earthquake": (598, 289), "poisoned_wind": (598, 289), "sylvan_power": (500, 341)},
                       "blue": {"earthquake": (632, 408), "poisoned_wind": (632, 408), "sylvan_power": (532, 358)}},
            "0,-28" : {"red" : {"earthquake": (633, 306), "poisoned_wind": (633, 306), "sylvan_power": (531, 357)},
                       "blue": {"earthquake": (666, 391), "poisoned_wind": (666, 391), "sylvan_power": (565, 340)}},
            "-2,-28": {"red" : {"earthquake": {(400, 355): (431, 344), (534, 355): (431, 344)}, "poisoned_wind": {(400, 355): (431, 344), (534, 355): (431, 344)}, "sylvan_power": {(400, 355): (400, 355), (534, 355): (504, 374)}},
                       "blue": {"earthquake": {(468, 322): (431, 344), (468, 357): (431, 344)}, "poisoned_wind": {(468, 322): (431, 344), (468, 357): (431, 344)}, "sylvan_power": {(468, 322): (468, 322), (468, 357): (468, 357)}}},
        }

    @staticmethod
    def get_starting_cells():
        return {
            "3,-25" : {"red": [(234, 237), (267, 221)], "blue": [(700, 442), (733, 425)]},
            "3,-26" : {"red": [(568, 236), (535, 219)], "blue": [(602, 423), (635, 440)]},
            "2,-26" : {"red": [(400, 186), (434, 169)], "blue": [(633, 272), (667, 289)]},
            "2,-27" : {"red": [(703, 372), (735, 356)], "blue": [(468, 254), (502, 237)]},
            "2,-28" : {"red": [(535, 356), (567, 339)], "blue": [(602, 389), (634, 372)]},
            "1,-28" : {"red": [(266, 323), (300, 306)], "blue": [(433, 408), (467, 424)]},
            "1,-27" : {"red": [(636, 372), (670, 388)], "blue": [(135, 219), (101, 202)]},
            "1,-26" : {"red": [(533, 187), (601, 186)], "blue": [(667, 390), (634, 407)]},
            "1,-25" : {"red": [(601, 458), (567, 474)], "blue": [(601, 288), (667, 288)]},
            "2,-25" : {"red": [(400, 220), (433, 204)], "blue": [(500, 373), (533, 357)]},
            "2,-24" : {"red": [(533, 391), (567, 374)], "blue": [(667, 425), (700, 408)]},
            "1,-24" : {"red": [(467, 390), (500, 374)], "blue": [(200, 254), (234, 237)]},
            "0,-24" : {"red": [(334, 220), (367, 170)], "blue": [(633, 238), (600, 289)]},
            "0,-25" : {"red": [(436, 439), (502, 439)], "blue": [(535, 253), (602, 254)]},
            "0,-28" : {"red": [(469, 457), (536, 456)], "blue": [(636, 236), (770, 236)]},
            "-2,-28": {"red": [(400, 355), (534, 355)], "blue": [(468, 322), (468, 357)]},
            "-2,-26": {"red": [(504, 474), (540, 492)], "blue": [(802, 287), (835, 304)]},
            "-2,-24": {"red": [(468, 319), (500, 305)], "blue": [(567, 305), (434, 373)]},
            "-1,-23": {"red": [(769, 440), (803, 423)], "blue": [(536, 320), (602, 355)]},
            "1,-23" : {"red": [(400, 357), (434, 374)], "blue": [(667, 288), (633, 272)]},
        }

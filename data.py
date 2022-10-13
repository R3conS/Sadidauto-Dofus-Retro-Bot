"""Holds various data classes."""

#----------------------------------------------------------------------#
#---------------------------DETECTION RELATED--------------------------#
#----------------------------------------------------------------------#


class ImageData:
    """Holds image data."""

    # Test images.
    test_monster_images_path = "test_monster_images\\"
    test_monster_images_list = ["test_1.jpg", "test_2.jpg", 
                                "test_3.jpg", "test_4.jpg"]

    # Status images path.
    s_i = "status_images\\"

    # Amakna Castle Gobbals.
    acg_images_path = "monster_images\\amakna_castle_gobballs\\"
    acg_images_list = [
            "Gobball_BL_1.jpg", "Gobball_BR_1.jpg", 
            "Gobball_TL_1.jpg", "Gobball_TR_1.jpg",
            "GobblyBlack_BL_1.jpg", "GobblyBlack_BR_1.jpg",
            "GobblyBlack_TL_1.jpg", "GobblyBlack_TR_1.jpg",
            "GobblyWhite_BL_1.jpg", "GobblyWhite_BR_1.jpg",
            "GobblyWhite_TL_1.jpg", "GobblyWhite_TR_1.jpg",
        ]

    # Astrub Forest.
    af_images_path = "monster_images\\astrub_forest\\"
    af_images_list = [
            "Boar_BL_1.jpg", "Boar_BR_1.jpg", "Boar_TL_1.jpg", "Boar_TR_1.jpg",
            "Boar_BL_2.jpg", "Boar_BR_2.jpg", "Boar_TL_2.jpg", "Boar_TR_2.jpg",
            "Boar_BL_3.jpg", "Boar_BR_3.jpg", "Boar_TL_3.jpg", "Boar_TR_3.jpg",
            "Boar_BL_4.jpg", "Boar_BR_4.jpg", "Boar_TL_4.jpg", "Boar_TR_4.jpg",

            "Mosk_BL_1.jpg", "Mosk_BR_1.jpg", "Mosk_TL_1.jpg", "Mosk_TR_1.jpg",
            "Mosk_BL_2.jpg", "Mosk_BR_2.jpg", "Mosk_TL_2.jpg", "Mosk_TR_2.jpg",
            "Mosk_BL_3.jpg", "Mosk_BR_3.jpg", "Mosk_TL_3.jpg", "Mosk_TR_3.jpg",
            "Mosk_BL_4.jpg", "Mosk_BR_4.jpg", "Mosk_TL_4.jpg", "Mosk_TR_4.jpg", 

            "Mush_BL_1.jpg", "Mush_BR_1.jpg", "Mush_TL_1.jpg", "Mush_TR_1.jpg",
            "Mush_BL_2.jpg", "Mush_BR_2.jpg", "Mush_TL_2.jpg", "Mush_TR_2.jpg",
            "Mush_BL_3.jpg", "Mush_BR_3.jpg", "Mush_TL_3.jpg", "Mush_TR_3.jpg",
            "Mush_BL_4.jpg", "Mush_BR_4.jpg", "Mush_TL_4.jpg", "Mush_TR_4.jpg",

            "Pres_BL_1.jpg", "Pres_BR_1.jpg", "Pres_TL_1.jpg", "Pres_TR_1.jpg",
            "Pres_BL_2.jpg", "Pres_BR_2.jpg", "Pres_TL_2.jpg", "Pres_TR_2.jpg",
            "Pres_BL_3.jpg", "Pres_BR_3.jpg", "Pres_TL_3.jpg", "Pres_TR_3.jpg",
            "Pres_BL_4.jpg", "Pres_BR_4.jpg", "Pres_TL_4.jpg", "Pres_TR_4.jpg",

            "Wolf_BL_1.jpg", "Wolf_BR_1.jpg", "Wolf_TL_1.jpg", "Wolf_TR_1.jpg",
            "Wolf_BL_2.jpg", "Wolf_BR_2.jpg", "Wolf_TL_2.jpg", "Wolf_TR_2.jpg",
            "Wolf_BL_3.jpg", "Wolf_BR_3.jpg", "Wolf_TL_3.jpg", "Wolf_TR_3.jpg",
            "Wolf_BL_4.jpg", "Wolf_BR_4.jpg", "Wolf_TL_4.jpg", "Wolf_TR_4.jpg",
        ]


#----------------------------------------------------------------------#
#---------------------------MOVEMENT RELATED---------------------------#
#----------------------------------------------------------------------#


class MapData:
    """
    Holds map data.
    
    - When adding cell coordinates to maps, the first two coordinates 
    must be red color cells and the last two must be blue. A total of 
    4 cells is accepted. 
    - Character must be highlighted (white) when the coordinates 
    (of cells) are clicked/hovered on. This makes script able to check
    whether character was moved. Make sure character is highlighted 
    both mounted and not.
    - Select cell coordinates that cannot be blocked by random 
    char/monster placement when joining fight. The blue/red pixel 
    on the cell coordinate must be visible during selection.

    Map types
    ----------
    - Fightable - character will search for monsters and fight on it.
    - Traversable - character will run through it without fighting.
    
    """

    # 'Astrub Forest' script map data for hunting mobs.
    af_killing = [
        # 'Astrub Bank' map.
        {"4,-16" : {"top" : (467, 87), "exit_bank": (266, 495),
                    "map_type": "traversable"}},
        {"4,-17" : {"top"   : (434, 71),  "map_type": "traversable"}},
        {"4,-18" : {"top"   : (499, 70),  "map_type": "traversable"}},
        {"4,-19" : {"top"   : (501, 69),  "map_type": "traversable"}},
        {"4,-20" : {"top"   : (433, 70),  "map_type": "traversable"}},
        {"4,-21" : {"right" : (901, 376), "map_type": "traversable"}},
        {"5,-21" : {"top"   : (367, 69),  "map_type": "traversable"}},
        {"5,-22" : {"top"   : (566, 69),  "map_type": "traversable"}},
        {"5,-23" : {"left"  : (34, 342),  "map_type": "traversable"}},
        {"4,-23" : {"left"  : (33, 307),  "map_type": "traversable"}},
        {"3,-23" : {"top"   : (434, 69),  "map_type": "traversable"}},
        {"3,-24" : {"top"   : (299, 69),  "map_type": "traversable"}},
        {"3,-25" : {"top"   : (500, 70),  "map_type": "fightable",
                    "cell"  : [(227, 241),(260, 224),(694, 444),(727, 427)]}},
        {"3,-26" : {"left"  : (32, 342),  "map_type": "fightable",
                    "cell"  : [(559, 240),(528, 224),(594, 427),(627, 444)]}},
        {"2,-26" : {"top"   : (300, 69),  "map_type": "fightable",
                    "cell"  : [(395, 188),(427, 172),(626, 274),(659, 291)]}},
        {"2,-27" : {"top"   : (567, 70),  "map_type": "traversable"}},
        {"2,-28" : {"left"  : (34, 443),  "map_type": "fightable",
                    "cell"  : [(528, 359),(561, 343),(595, 393),(627, 375)]}},
        {"1,-28" : {"bottom": (34, 443),  "map_type": "fightable",
                    "cell"  : [(261, 326),(294, 310),(426, 410),(458, 426)]}},
        {"1,-27" : {"bottom": (566, 580), "map_type": "traversable"}},
        {"1,-26" : {"bottom": (633, 580), "map_type": "fightable",
                    "cell"  : [(527, 189),(594, 190),(661, 393),(626, 410)]}},
        {"1,-25" : {"right" : (901, 444), "map_type": "fightable",
                    "cell"  : [(595, 461),(561, 478),(594, 292),(661, 291)]}},
        {"2,-25" : {"bottom": (567, 580), "map_type": "fightable",
                    "cell"  : [(393, 224),(427, 207),(493, 376),(526, 359)]}},
        {"2,-24" : {"left"  : (33, 307),  "map_type": "fightable",
                    "cell"  : [(527, 393),(561, 378),(660, 428),(694, 412)]}},
        {"1,-24" : {"left"  : (33, 342),  "map_type": "fightable",
                    "cell"  : [(461, 394),(493, 375),(194, 257),(227, 240)]}},
        {"0,-24" : {"top"   : (434, 70),  "map_type": "fightable",
                    "cell"  : [(327, 224),(372, 168),(638, 236),(604, 287)]}},
        {"0,-25" : {"left"  : (32, 308),  "map_type": "traversable"}},
        {"-1,-25": {"top"   : (433, 71),  "map_type": "traversable"}},
        {"-1,-26": {"left"  : (33, 341),  "map_type": "traversable"}},
        {"-2,-26": {"bottom": (433, 581), "map_type": "fightable",
                    "cell"  : [(504, 474),(540, 492),(794, 292),(827, 307)]}},
        {"-2,-25": {"bottom": (500, 582), "map_type": "traversable"}},
        {"-2,-24": {"right" : (901, 309), "map_type": "fightable",
                    "cell"  : [(461, 325),(493, 308),(560, 308),(427, 376)]}},
        {"-1,-24": {"bottom": (433, 579), "map_type": "traversable"}},
        {"-1,-23": {"right" : (901, 274), "map_type": "fightable",
                    "cell"  : [(761, 445),(794, 428),(526, 326),(594, 359)]}},
        {"0,-23" : {"right" : (901, 343), "map_type": "traversable"}},
        {"1,-23" : {"right" : (901, 410), "map_type": "fightable",
                    "cell"  : [(394, 360),(427, 376),(661, 291),(627, 274)]}},
        {"2,-23" : {"right" : (901, 308), "map_type": "traversable"}},
    ]

    # 'Astrub Forest' script map data for banking.
    af_banking = [
        # TO DO
    ]

#----------------------------------------------------------------------#
#----------------------------COMBAT RELATED----------------------------#
#----------------------------------------------------------------------#


class CombatData:
    """Holds paths, verifiers."""

    images_path = "combat_images\\"
    icon_turn_pass = images_path + "icon_turn_pass.jpg"


class SpellData:
    """
    Holds spell data.
    
    Format
    ----------
    If value of 'e', 'p' or 's' is ONLY a tuple:
        (coordinates to click on to cast spell)
    If value of 'e', 'p' or 's' is a dictionary:
        {(start cell coordinates): (coords to click on to cast spell)}

    """

    # Spell paths.
    e_quake = CombatData.images_path + "earthquake.jpg"
    p_wind = CombatData.images_path + "poisoned_wind.jpg"
    s_power = CombatData.images_path + "sylvan_power.jpg"
    spells = [e_quake, p_wind, s_power]

    # Spell cast data for 'Astrub Forest' script.
    af = [
        {"3,-25" : {"r": {"e": {(227, 241): (466, 359),
                                (260, 224): (499, 342)},
                          "p": {(227, 241): (466, 359),
                                (260, 224): (499, 342)},
                          "s": {(227, 241): (365, 308),
                                (260, 224): (400, 291)}},
                    "b": {"e": {(694, 444): (464, 325),
                                (727, 427): (496, 306)},
                          "p": {(694, 444): (464, 325),
                                (727, 427): (496, 306)},
                          "s": {(694, 444): (567, 375),
                                (727, 427): (597, 358)}}}},
        {"3,-26" : {"r": {"e": (631, 340), "p": (631, 340), "s": (532, 290)},
                    "b": {"e": (599, 322), "p": (599, 322), "s": (499, 374)}}},
        {"2,-26" : {"r": {"e": (499, 240), "p": (499, 240), "s": (499, 240)},
                    "b": {"e": (531, 223), "p": (531, 223), "s": (531, 223)}}},
        {"2,-28" : {"r": {"e": (632, 407), "p": (632, 407), "s": (527, 361)},
                    "b": {"e": (498, 341), "p": (498, 341), "s": (593, 393)}}},
        {"1,-28" : {"r": {"e": (260, 326), "p": (260, 326), "s": (260, 326)},
                    "b": {"e": (427, 409), "p": (427, 409), "s": (427, 409)}}},
        {"1,-26" : {"r": {"e": (498, 308), "p": (498, 308), "s": (599, 257)},
                    "b": {"e": (667, 288), "p": (667, 288), "s": (766, 341)}}},
        {"1,-25" : {"r": {"e": (599, 359), "p": (599, 359), "s": (698, 408)},
                    "b": {"e": (665, 358), "p": (665, 358), "s": (665, 358)}}},
        {"2,-25" : {"r": {"e": (395, 225), "p": (395, 225), "s": (395, 225)},
                    "b": {"e": (399, 323), "p": (399, 323), "s": (494, 376)}}},
        {"2,-24" : {"r": {"e": (527, 393), "p": (527, 393), "s": (527, 393)},
                    "b": {"e": (660, 428), "p": (660, 428), "s": (660, 428)}}},
        {"1,-24" : {"r": {"e": (366, 342), "p": (366, 342), "s": (461, 394)},
                    "b": {"e": (299, 308), "p": (299, 308), "s": (194, 257)}}},
        {"0,-24" : {"r": {"e": (531, 291), "p": (531, 291), "s": (432, 239)},
                    "b": {"e": (399, 188), "p": (399, 188), "s": (499, 239)}}},
        {"-2,-26": {"r": {"e": (598, 426), "p": (598, 426), "s": (504, 474)},
                    "b": {"e": (599, 393), "p": (599, 393), "s": (699, 341)}}},
        {"-2,-24": {"r": {"e": (461, 325), "p": (461, 325), "s": (461, 325)},
                    "b": {"e": {(560, 308): (560, 308),
                                (427, 376): (427, 376)},
                          "p": {(560, 308): (560, 308),
                                (427, 376): (427, 376)},
                          "s": {(560, 308): (560, 308),
                                (427, 376): (427, 376)}}}},
        {"-1,-23": {"r": {"e": (761, 445), "p": (761, 445), "s": (761, 445)},
                    "b": {"e": (498, 308), "p": (498, 308), "s": (498, 308)}}},
        {"1,-23" : {"r": {"e": (394, 360), "p": (394, 360), "s": (394, 360)},
                    "b": {"e": (661, 291), "p": (661, 291), "s": (661, 291)}}},
    ]


class MovementData:
    """
    Holds data for in-combat movement.
    
    Format
    ----------
    If value of 'red' or 'blue' is ONLY a tuple:
        (x, y coordinates of starting cell)
    If value of 'red' or 'blue' is a dictionary:
        {(x, y coordinates of starting cell): (coordinates to click on)}
    
    """

    # Astrub Forest.
    af = [
        {"3,-25" : {"red" : {(227, 241): (365, 308),
                             (260, 224): (400, 291)},
                    "blue": {(694, 444): (567, 375),
                             (727, 427): (597, 358)}}},
        {"3,-26" : {"red" : (532, 290), "blue": (499, 374)}},
        {"2,-26" : {"red" : (499, 240), "blue": (531, 223)}},
        {"2,-28" : {"red" : (525, 358), "blue": (594, 393)}},
        {"1,-28" : {"red" : (260, 326), "blue": (427, 409)}},
        {"1,-26" : {"red" : (599, 257), "blue": (766, 342)}},
        {"1,-25" : {"red" : (698, 408), "blue": (665, 358)}},
        {"2,-25" : {"red" : (395, 225), "blue": (494, 376)}},
        {"2,-24" : {"red" : (527, 393), "blue": (660, 428)}},
        {"1,-24" : {"red" : (461, 394), "blue": (194, 257)}},
        {"0,-24" : {"red" : (432, 239), "blue": (499, 239)}},       
        {"-2,-26": {"red" : (504, 474), "blue": (699, 341)}},
        {"-2,-24": {"red" : (461, 325), 
                    "blue": {(560, 308): (560, 308),
                             (427, 376): (427, 376)}}},
        {"-1,-23": {"red" : (761, 445), "blue": (498, 308)}},
        {"1,-23" : {"red" : (394, 360), "blue": (661, 291)}},
    ]


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
    
    When adding cell coordinates to maps, the first two coordinates must 
    be red color cells and the last two must be blue. A total of 4 cells 
    is accepted.

    Map types:
    Fightable - character will search for monsters and fight on it.
    Traversable - character will run through it without fighting.
    
    """
    # Astrub Forest.
    af_killing = [
        {"2,-25": {"top" : (  None  ), "bottom": (  None  ),
                   "left": (  None  ), "right" : (900, 274),
                   "cell": [(393, 224), (427, 207), (493, 376), (526, 359)],
                   "map_type": "fightable"}},
        # Invalid data (except "left")
        {"3,-25": {"top" : (  None  ), "bottom": (  None  ),
                   "left": (33 , 274), "right" : (  None  ),
                   "cell": [(393, 224), (427, 207), (493, 376), (526, 359)],
                   "map_type": "traversable"}}
        # TO DO
    ]

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
    """Holds spell data."""

    # Spell paths.
    e_quake = CombatData.images_path + "earthquake.jpg"
    p_wind = CombatData.images_path + "poisoned_wind.jpg"
    s_power = CombatData.images_path + "sylvan_power.jpg"
    spells = [e_quake, p_wind, s_power]

    # Spell cast data for 'Astrub Forest'.
    af = [
        {"2,-25": {"r": {"e": (493, 275), "p": (493, 275), "s": (493, 275)}, 
                   "b": {"e": (394, 326), "p": (394, 326), "s": (394, 326)}}},
    ]


class MovementData:
    """Holds data for in-combat movement."""

    # Amakna Castle Gobballs
    acg = []

    # Astrub Forest.
    af = [
        {"2,-25": {"red": (493, 275), "blue": (394, 326)}},
    ]


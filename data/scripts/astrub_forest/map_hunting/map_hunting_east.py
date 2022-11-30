class East:
    """
    Holds map data.

    Pathing from Astrub Bank to multiple Astrub Forest maps.

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

    Cell types
    ----------
    - "cell" - character will start combat on one of these cells.
    - "d_cell" - character will move to one of these "dummy" cells 
    before trying to select starting "cell".

    Map types
    ----------
    - Fightable - character will search for monsters and fight on it.
    - Traversable - character will run through it without fighting.

    """

    data = [
        # 'Astrub Bank' map.
        {"4,-16" : {"top"    : (467, 87),  "map_type": "traversable"}},

        {"4,-17" : {"top"    : (434, 71),  "map_type": "traversable"}},

        {"4,-18" : {"top"    : (499, 70),  "map_type": "traversable"}},

        {"4,-19" : {"top"    : (501, 69),  "map_type": "traversable"}},

        {"4,-20" : {"top"    : (433, 70),  "map_type": "traversable"}},

        {"4,-21" : {"right"  : (901, 376), "map_type": "traversable"}},

        {"5,-21" : {"top"    : (367, 69),  "map_type": "traversable"}},

        {"5,-22" : {"top"    : (566, 69),  "map_type": "traversable"}},

        {"5,-23" : {"left"   : (34, 342),  "map_type": "traversable"}},

        {"4,-23" : {"left"   : (33, 307),  "map_type": "traversable"}},

        {"3,-23" : {"top"    : (434, 69),  "map_type": "traversable"}},

        {"3,-24" : {"top"    : (299, 69),  "map_type": "traversable"}},

        {"3,-25" : {"top"    : (500, 56),  "map_type": "fightable",
                    "cell"   : [(234, 237),(267, 221),(700, 442),(733, 425)]}},

        {"3,-26" : {"left"   : (8, 342),   "map_type": "fightable",
                    "cell"   : [(568, 236),(535, 219),(602, 423),(635, 440)]}},

        {"2,-26" : {"top"    : (300, 56),  "map_type": "fightable",
                    "cell"   : [(400, 186),(434, 169),(633, 272),(667, 289)]}},

        {"2,-27" : {"top"    : (565, 56),  "map_type": "fightable",
                    "cell"   : [(703, 372),(735, 356),(468, 254),(502, 237)]}},

        {"2,-28" : {"left"   : (8, 443),   "map_type": "fightable",
                    "cell"   : [(535, 356),(567, 339),(602, 389),(634, 372)]}},

        {"1,-28" : {"bottom" : (367, 580), "map_type": "fightable",
                    "cell"   : [(266, 323),(300, 306),(433, 408),(467, 424)]}},

        {"1,-27" : {"bottom" : (567, 589), "map_type": "fightable",
                    "cell"   : [(636, 372),(670, 388),(135, 219),(101, 202)]}},

        {"1,-26" : {"bottom" : (633, 580), "map_type": "fightable",
                    "cell"   : [(533, 187),(601, 186),(667, 390),(634, 407)]}},

        {"1,-25" : {"right"  : (926, 443), "map_type": "fightable",
                    "cell"   : [(601, 458),(567, 474),(601, 288),(667, 288)]}},

        {"2,-25" : {"right"  : (926, 275), "map_type": "fightable",
                    "cell"   : [(400, 220),(433, 204),(500, 373),(533, 357)]}},

        # Used only when map was changed accidentally during attack.
        {"4,-25"  : {"left"  : (8, 408),   "map_type": "traversable"}}, 

        {"4,-26"  : {"left"  : (4, 377),   "map_type": "traversable"}},

        {"3,-27"  : {"bottom": (700, 592), "map_type": "traversable",
                     "left"  : (6, 342)}},

        {"3,-28"  : {"left"  : (5, 342),   "map_type": "traversable"}},

        {"2,-29"  : {"bottom": (493, 588), "map_type": "traversable"}},

        {"0,-28"  : {"right" : (924, 239), "map_type": "traversable"}},

        {"0,-27"  : {"right" : (925, 410), "map_type": "traversable"}},

        {"0,-26"  : {"right" : (923, 410), "map_type": "traversable"}},

        {"0,-25"  : {"right" : (923, 410), "map_type": "traversable"}},

        {"1,-24"  : {"top"   : (432, 55),  "map_type": "traversable"}},

        {"2,-24"  : {"top"   : (566, 57),  "map_type": "traversable"}},
    ]

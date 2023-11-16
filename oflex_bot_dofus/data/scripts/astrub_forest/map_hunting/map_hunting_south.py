class South:
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

        {"3,-25" : {"left"   : (5, 274),   "map_type": "fightable",
                    "cell"   : [(234, 237),(267, 221),(700, 442),(733, 425)]}},

        {"2,-25" : {"left"   : (7, 443),   "map_type": "fightable",
                    "cell"   : [(400, 220),(433, 204),(500, 373),(533, 357)]}},

        {"1,-25" : {"left"   : (6, 410),   "map_type": "fightable",
                    "cell"   : [(601, 458),(567, 474),(601, 288),(667, 288)]}},      

        {"0,-25" : {"left"   : (8, 307),   "map_type": "fightable",
                    "cell"   : [(436, 439),(502, 439),(535, 253),(602, 254)],
                    "d_cell" : [(569, 474),(569, 507),(636, 473),(636, 508),
                                (602, 151),(535, 186),(469, 219),(602, 186)]}},

        {"-1,-25" : {"left"  : (5, 307),   "map_type": "traversable"}},

        {"-2,-25": {"bottom" : (496, 589), "map_type": "traversable"}},

        {"-2,-24": {"right"  : (926, 309), "map_type": "fightable",
                    "cell"   : [(468, 319),(500, 305),(567, 305),(434, 373)]}},

        {"-1,-24": {"bottom" : (433, 579), "map_type": "traversable"}},

        {"-1,-23": {"right"  : (926, 274), "map_type": "fightable",
                    "cell"   : [(769, 440),(803, 423),(536, 320),(602, 355)]}},

        {"0,-23" : {"top"    : (498, 56),  "map_type": "traversable"}},

        {"0,-24" : {"right"  : (926, 341), "map_type": "fightable",
                    "cell"   : [(334, 220),(367, 170),(633, 238),(600, 289)]}},

        {"1,-24" : {"bottom" : (482, 582), "map_type": "fightable",
                    "cell"   : [(467, 390),(500, 374),(200, 254),(234, 237)]}},

        {"1,-23" : {"right"  : (926, 410), "map_type": "fightable",
                    "cell"   : [(400, 357),(434, 374),(667, 288),(633, 272)]}},

        {"2,-23" : {"top"    : (296, 56),  "map_type": "traversable"}},

        {"2,-24" : {"right"  : (925, 374), "map_type": "fightable",
                    "cell"   : [(533, 391),(567, 374),(667, 425),(700, 408)]}},

        # Used only when map was changed accidentally during attack.
        {"4,-25"  : {"left"  : (8, 408),   "map_type": "traversable"}},

        {"3,-26"  : {"bottom": (485, 584), "map_type": "traversable"}},

        {"2,-26"  : {"bottom": (366, 590), "map_type": "traversable"}},

        {"1,-26"  : {"bottom": (633, 588), "map_type": "traversable"}},

        {"0,-26"  : {"bottom": (366, 589), "map_type": "traversable"}},

        {"-3,-24" : {"right" : (930, 308), "map_type": "traversable"}},

        {"-2,-23" : {"top"   : (500, 55),  "map_type": "traversable",
                     "right" : (925, 375)}},

        {"-1,-22" : {"top"   : (500, 56),  "map_type": "traversable"}},
    ]

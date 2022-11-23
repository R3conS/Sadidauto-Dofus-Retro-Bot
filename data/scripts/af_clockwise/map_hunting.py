class Hunting:
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

    Map types
    ----------
    - Fightable - character will search for monsters and fight on it.
    - Traversable - character will run through it without fighting.
    
    """

    data = [
        {"4,-16" : {"left"   : (33, 341),  "map_type": "traversable"}},
        {"3,-16" : {"left"   : (32, 274),  "map_type": "traversable"}},
        {"2,-16" : {"left"   : (33, 342),  "map_type": "traversable"}},
        {"1,-16" : {"left"   : (31, 274),  "map_type": "traversable"}},
        {"0,-16" : {"top"    : (300, 70),  "map_type": "traversable"}},
        {"0,-17" : {"top"    : (500, 70),  "map_type": "traversable"}},
        {"0,-18" : {"top"    : (432, 70),  "map_type": "traversable"}},
        {"0,-19" : {"top"    : (434, 70),  "map_type": "traversable"}},
        {"0,-20" : {"left"   : (31, 308),  "map_type": "traversable"}},
        {"-1,-20": {"left"   : (32, 376),  "map_type": "traversable"}},
        {"-2,-20": {"top"    : (500, 70),  "map_type": "traversable"}},
        {"-2,-21": {"top"    : (500, 70),  "map_type": "traversable"}},
        {"-2,-22": {"top"    : (500, 70),  "map_type": "traversable"}},
        {"-2,-23": {"top"    : (500, 70),  "map_type": "traversable"}},
        {"-2,-24": {"top"    : (432, 56),  "map_type": "fightable",
                    "cell"   : [(468, 319),(500, 305),(567, 305),(434, 373)]}},
        {"-2,-25": {"top"    : (501, 66),  "map_type": "traversable"}},
        {"-2,-26": {"right"  : (926, 306), "map_type": "fightable",
                    "cell"   : [(504, 474),(540, 492),(802, 287),(835, 304)]}},
        {"-1,-26": {"bottom" : (433, 580), "map_type": "traversable"}},
        {"-1,-25": {"right"  : (900, 307), "map_type": "traversable"}},
        {"0,-25" : {"bottom" : (433, 583), "map_type": "traversable"}},
        {"0,-24" : {"right"  : (926, 341), "map_type": "fightable",
                    "cell"   : [(334, 220),(367, 170),(633, 238),(600, 289)]}},
        {"1,-24" : {"right"  : (929, 308), "map_type": "fightable",
                    "cell"   : [(467, 390),(500, 374),(200, 254),(234, 237)]}},
        {"2,-24" : {"top"    : (568, 57),  "map_type": "fightable",
                    "cell"   : [(533, 391),(567, 374),(667, 425),(700, 408)]}},
        {"2,-25" : {"left"   : (7, 444),   "map_type": "fightable",
                    "cell"   : [(400, 220),(433, 204),(500, 373),(533, 357)]}},
        {"1,-25" : {"top"    : (635, 56),  "map_type": "fightable",
                    "cell"   : [(601, 458),(567, 474),(601, 288),(667, 288)]}},
        {"1,-26" : {"top"    : (568, 56),  "map_type": "fightable",
                    "cell"   : [(533, 187),(601, 186),(667, 390),(634, 407)]}},
        {"1,-27" : {"top"    : (367, 70),  "map_type": "traversable"}},
        {"1,-28" : {"right"  : (927, 442), "map_type": "fightable",
                    "cell"   : [(266, 323),(300, 306),(433, 408),(467, 424)]}},
        {"2,-28" : {"bottom" : (567, 581), "map_type": "fightable",
                    "cell"   : [(535, 356),(567, 339),(602, 389),(634, 372)]}},
        {"2,-27" : {"bottom" : (300, 580), "map_type": "traversable"}},
        {"2,-26" : {"right"  : (928, 341), "map_type": "fightable",
                    "cell"   : [(400, 186),(434, 169),(633, 272),(667, 289)]}},
        {"3,-26" : {"bottom" : (500, 580), "map_type": "fightable",
                    "cell"   : [(568, 236),(535, 219),(602, 423),(635, 440)]}},
        {"3,-25" : {"bottom" : (300, 580), "map_type": "fightable",
                    "cell"   : [(234, 237),(267, 221),(700, 442),(733, 425)]}},
        {"3,-24" : {"bottom" : (433, 581), "map_type": "traversable"}},
        {"3,-23" : {"left"   : (32, 308),  "map_type": "traversable"}},
        {"2,-23" : {"left"   : (32, 409),  "map_type": "traversable"}},
        {"1,-23" : {"left"   : (7, 307),   "map_type": "fightable",
                    "cell"   : [(400, 357),(434, 374),(667, 288),(633, 272)]}},
        {"0,-23" : {"left"   : (32, 308),  "map_type": "traversable"}},
        {"-1,-23": {"left"   : (7, 307),   "map_type": "fightable",
                    "cell"   : [(769, 440),(803, 423),(536, 320),(602, 355)]}},
        # Used only when map was changed accidentally during attack.
        {"-1,-22" : {"top"   : (500, 56),  "map_type": "traversable"}},
        {"-1,-24" : {"left"  : (33, 342),  "map_type": "traversable"}},
        {"-3,-24" : {"right" : (930, 308), "map_type": "traversable"}},
        {"-3,-26" : {"right" : (930, 308), "map_type": "traversable"}},
        {"-2,-27" : {"bottom": (433, 593), "map_type": "traversable"}},
        {"0,-26"  : {"right" : (928, 411), "map_type": "traversable"}},
        {"0,-28"  : {"right" : (927, 240), "map_type": "traversable"}},
        {"2,-29"  : {"bottom": (493, 588), "map_type": "traversable"}},
        {"3,-28"  : {"left"  : (5, 342),   "map_type": "traversable"}},
        {"3,-27"  : {"bottom": (700, 592), "map_type": "traversable"}},
        {"4,-26"  : {"left"  : (4, 377),   "map_type": "traversable"}},
        {"4,-25"  : {"left"  : (8, 408),   "map_type": "traversable"}},
    ]

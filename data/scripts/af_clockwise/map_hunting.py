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
        # 'Astrub Bank' map.
        {"4,-16" : {"top"    : (467, 87),  "map_type": "traversable"}},

        {"4,-17" : {"top"    : (434, 71),  "map_type": "traversable"}},

        {"4,-18" : {"top"    : (499, 70),  "map_type": "traversable"}},

        {"4,-19" : {"top"    : (501, 69),  "map_type": "traversable"}},

        {"4,-20" : {"left"   : (5, 375),   "map_type": "traversable"}},

        {"3,-20" : {"left"   : (7, 309),   "map_type": "traversable"}},

        {"2,-20" : {"left"   : (6, 377),   "map_type": "traversable"}},

        {"1,-20" : {"left"   : (4, 343),   "map_type": "traversable"}},

        {"0,-20" : {"left"   : (31, 308),  "map_type": "traversable"}},

        {"-1,-20": {"left"   : (32, 376),  "map_type": "traversable"}},

        {"-2,-20": {"top"    : (500, 70),  "map_type": "traversable"}},

        {"-2,-21": {"top"    : (500, 70),  "map_type": "traversable"}},

        {"-2,-22": {"top"    : (500, 70),  "map_type": "traversable"}},

        {"-2,-24": {"top"    : (432, 56),  "map_type": "fightable",
                    "cell"   : [(468, 319),(500, 305),(567, 305),(434, 373)]}},

        {"-2,-25": {"top"    : (501, 66),  "map_type": "traversable"}},

        {"-2,-26": {"top"    : (432, 57),  "map_type": "fightable",
                    "cell"   : [(504, 474),(540, 492),(802, 287),(835, 304)]}},

        {"-2,-27": {"top"    : (432, 56),  "map_type": "traversable"}},

        {"-2,-28": {"right"  : (928, 307), "map_type": "fightable",
                    "cell"   : [(400, 355),(534, 355),(468, 322),(468, 357)],
                    "d_cell" : [(201, 457),(235, 474),(702, 236),(669, 218),
                                (468, 492),(468, 458),(468, 220),(468, 186)]}},

        {"-1,-28": {"right"  : (927, 307), "map_type": "traversable"}},

        {"0,-28" : {"bottom" : (433, 593), "map_type": "fightable",
                    "cell"   : [(469, 457),(536, 456),(636, 236),(770, 236)]}},

        {"0,-27" : {"bottom" : (433, 593), "map_type": "traversable"}},

        {"0,-26" : {"bottom" : (367, 591), "map_type": "traversable"}},

        {"0,-25" : {"bottom" : (433, 592), "map_type": "fightable",
                    "cell"   : [(436, 439),(502, 439),(535, 253),(602, 254)],
                    "d_cell" : [(569, 474),(569, 507),(636, 473),(636, 508),
                                (602, 151),(535, 186),(469, 219),(602, 186)]}},

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

        {"1,-27" : {"top"    : (367, 70),  "map_type": "fightable",
                    "cell"   : [(636, 372),(670, 388),(135, 219),(101, 202)]}},

        {"1,-28" : {"right"  : (927, 442), "map_type": "fightable",
                    "cell"   : [(266, 323),(300, 306),(433, 408),(467, 424)]}},

        {"2,-28" : {"bottom" : (567, 581), "map_type": "fightable",
                    "cell"   : [(535, 356),(567, 339),(602, 389),(634, 372)]}},

        {"2,-27" : {"bottom" : (300, 580),  "map_type": "fightable",
                    "cell"   : [(703, 372),(735, 356),(468, 254),(502, 237)]}},

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

        {"-1,-23": {"top"    : (432, 56),   "map_type": "fightable",
                    "cell"   : [(769, 440),(803, 423),(536, 320),(602, 355)]}},
        
        {"-1,-24": {"left"   : (6, 342), "map_type": "traversable"}},

        # Used only when map was changed accidentally during attack.
        {"-1,-22" : {"top"   : (500, 56),  "map_type": "traversable"}},

        {"-2,-23" : {"top"   : (500, 55),  "right": (925, 375), 
                     "map_type": "traversable"}},

        {"-3,-24" : {"right" : (930, 308), "map_type": "traversable"}},

        {"-3,-26" : {"right" : (930, 308), "map_type": "traversable"}},

        {"-3,-28" : {"right" : (925, 308), "map_type": "traversable"}},

        {"-2,-29" : {"bottom": (433, 592), "map_type": "traversable"}},

        {"-1,-26" : {"left"  : (5, 341),   "right": (927, 307), 
                     "map_type": "traversable"}},

        {"-1,-25" : {"left"  : (5, 307),   "right": (926, 307), 
                     "map_type": "traversable"}},

        {"2,-29"  : {"bottom": (493, 588), "map_type": "traversable"}},

        {"3,-28"  : {"left"  : (5, 342),   "map_type": "traversable"}},

        {"3,-27"  : {"bottom": (700, 592), "left": (6, 342),
                     "map_type": "traversable"}},

        {"4,-26"  : {"left"  : (4, 377),   "map_type": "traversable"}},

        {"4,-25"  : {"left"  : (8, 408),   "map_type": "traversable"}},
    ]

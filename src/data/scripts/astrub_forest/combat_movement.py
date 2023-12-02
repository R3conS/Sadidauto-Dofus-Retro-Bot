class Movement:
    """
    Holds data for in-combat movement.
    
    Format
    ----------
    If value of 'red' or 'blue' is ONLY a tuple:
        (x, y coordinates of starting cell)
    If value of 'red' or 'blue' is a dictionary:
        {(x, y coordinates of starting cell): (coordinates to click on)}
    
    """
    
    data = [
        {"3,-25" : {"red" : {(234, 237): (365, 308), (267, 221): (400, 291)}, "blue": {(700, 442): (567, 375), (733, 425): (597, 358)}}},
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
        {"-2,-24": {"red" : (461, 325), "blue": {(567, 305): (560, 308), (434, 373): (427, 376)}}},
        {"-1,-23": {"red" : (761, 445), "blue": (498, 308)}},
        {"1,-23" : {"red" : (394, 360), "blue": (661, 291)}},
        {"2,-27" : {"red" : (531, 324), "blue": (567, 340)}},
        {"1,-27" : {"red" : (465, 290), "blue": (299, 307)}},
        {"0,-25" : {"red" : (500, 341), "blue": (532, 358)}},
        {"0,-28" : {"red" : (531, 357), "blue": (565, 340)}},
        {"-2,-28": {"red" : {(400, 355): (400, 355), (534, 355): (505, 375)}, "blue": {(468, 322): (468, 322), (468, 357): (468, 357)}}},
    ]

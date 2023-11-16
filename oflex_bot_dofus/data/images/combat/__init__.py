"""Combat related images."""

class Combat:
    """Combat images."""
    path = "oflex_bot_dofus\\data\\images\\combat\\"
    red_circle_1 = "red_circle_1.png"
    red_circle_2 = "red_circle_2.png"
    red_circle_3 = "red_circle_3.png"
    red_circle_4 = "red_circle_4.png"
    red_circle_5 = "red_circle_5.png"
    red_circle_6 = "red_circle_6.png"
    blue_circle = "blue_circle_1.png"
    a_sword = "ally_sword.png"
    m_sword = "monster_sword.png"
    spell_border = "spell_border.png"

    class Spell:
        """Spell images."""
        
        class Sadida:
            """Sadida spells."""
            path = "oflex_bot_dofus\\data\\images\\combat\\"
            earthquake = path + "earthquake.jpg"
            poisoned_wind = path + "poisoned_wind.jpg"
            sylvan_power = path + "sylvan_power.jpg"

            # Spell icons that appear when spell is selected and mouse
            # is hovered over on tiles, character etc.
            s_earthquake = path + "selected_earthquake.jpg"
            s_poisoned_wind = path + "selected_poisoned_wind.jpg"
            s_sylvan_power = path + "selected_sylvan_power.jpg"

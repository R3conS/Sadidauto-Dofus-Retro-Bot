from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import os

from ._spell import Spell


class Spells:

    _IMAGE_FOLDER_PATH = "src\\bot\\states\\in_combat\\sub_state\\fighting\\_spells\\images"
    EARTHQUAKE = Spell("Earthquake", os.path.join(_IMAGE_FOLDER_PATH, "earthquake"))
    POISONED_WIND = Spell("Poisoned Wind", os.path.join(_IMAGE_FOLDER_PATH, "poisoned_wind"))
    SYLVAN_POWER = Spell("Sylvan Power", os.path.join(_IMAGE_FOLDER_PATH, "sylvan_power"))
    BRAMBLE = Spell("Bramble", os.path.join(_IMAGE_FOLDER_PATH, "bramble"))

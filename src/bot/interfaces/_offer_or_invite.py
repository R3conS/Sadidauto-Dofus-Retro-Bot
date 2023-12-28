from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

from pyautogui import pixelMatchesColor

from ._interface import Interface


class OfferOrInvite:
    """Exchange, challenge offers & guild, group invites."""

    def __init__(self):
        self._name = "Offer or Invite"
        self._interface = Interface(self._name)

    def close(self):
        return self._interface.close(466, 387, self.is_open)
        
    def is_open():
        return all((
            pixelMatchesColor(406, 255, (81, 74, 60)),
            pixelMatchesColor(530, 255, (81, 74, 60)),
            pixelMatchesColor(284, 354, (213, 207, 170)),
            pixelMatchesColor(655, 354, (213, 207, 170)),
            pixelMatchesColor(427, 350, (255, 97, 0)),
            pixelMatchesColor(513, 350, (255, 97, 0))
        ))

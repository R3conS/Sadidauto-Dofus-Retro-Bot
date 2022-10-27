"""Provides Dofus's game window manipulating functionality."""

from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.INFO, True)

import pygetwindow as gw


class GameWindow:
    """
    Holds methods related to working with 'Dofus.exe' window.

    Instance attributes
    ----------
    character_name : str
        Character's nickname.
    official_version : bool
        Controls whether playing on official or private 'Dofus
        Retro' servers. Official = `True`.

    Methods
    ----------
    check_if_exists()
        Detect 'Dofus.exe' window.
    resize_and_move()
        Resize and move 'Dofus.exe' window.

    """

    def __init__(self, character_name: str, official_version: bool):
        """
        Constructor.

        Parameters
        ----------
        character_name : str
            Character's nickname.
        official_version : bool
            Controls whether playing on official or private 'Dofus
            Retro' servers. Official = `True`.
        
        """
        self.character_name = character_name
        self.official_version = official_version

    def check_if_exists(self) -> bool:
        """
        Detect 'Dofus.exe' window.
        
        Returns
        ----------
        True : bool
            If window was detected succesfully.
        False : bool
            If window wasn't detected.

        """
        gmw = gw.getWindowsWithTitle(self.character_name + " - Dofus Retro")
        if gmw:
            log.info("Game window successfully detected!")
            return True
        else:
            log.info("Couldn't find the game window. Please enter a valid"
                     "character name and make sure you are logged in.")
            return False

    def resize_and_move(self) -> None:
        """Resize and move 'Dofus.exe' window."""
        dfw = gw.getWindowsWithTitle(self.character_name + " - Dofus Retro")[0]
        dfw.restore()
        dfw.activate()

        if not self.official_version:
            # For Ascalion.
            dfw.resizeTo(950, 765) 
        elif self.official_version:
            # For Official Dofus Retro.
            dfw.resizeTo(950, 785)

        dfw.moveTo(-8, 0)

import pygetwindow as gw


class GameWindow:


    def __init__(self, character_name, official_version=False):

        # Character name.
        self.character_name = character_name
        # If 'false', means Ascalion.
        self.official_version = official_version


    # Checks if Dofus Retro window is running.
    def gamewindow_checkifexists(self):

        gameWindow = gw.getWindowsWithTitle(self.character_name + " - Dofus Retro")
        
        if gameWindow:
            print("Game window was successfully detected.\n")
            return True
        else:
            print("Couldn't find the game window. Please enter character name and make sure you are logged in.\n")
            return False


    # Resizes Dofus Retro window
    def gamewindow_resize(self):

        dofus_window = gw.getWindowsWithTitle(self.character_name + " - Dofus Retro")[0]
        dofus_window.restore()
        dofus_window.activate()

        if not self.official_version:
            # For Ascalion. Resizing to (w950, h765). These values should never be changed.
            dofus_window.resizeTo(950, 765) 
        elif self.official_version:
            # For Official Dofus Retro.
            dofus_window.resizeTo(950, 785) 

        dofus_window.moveTo(-8, 0)

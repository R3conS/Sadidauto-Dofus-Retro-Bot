import pygetwindow as gw


class GameWindow:


    def __init__(self, character_name, game_version):

        # Character name and game version
        self.character_name = character_name
        self.game_version = game_version


    # Checks if Dofus Retro window is running. If no character_name and game_version was given it will run for Ascalion.
    def gamewindow_checkifexists(self):

        gameWindow = gw.getWindowsWithTitle(self.character_name + " - Dofus Retro " + self.game_version)
        
        if gameWindow:
            print("Game window was successfully detected.\n")
            return True
        else:
            print("Couldn't find the game window. Please enter character name and make sure you are logged in.\n")
            return False


    # Resizes Dofus Retro window
    def gamewindow_resize(self):

        dofus_window = gw.getWindowsWithTitle("Dofus Retro")[0]
        dofus_window.restore()
        dofus_window.activate()
        # Resizing to (w950, h765). These values should never be changed.
        dofus_window.resizeTo(950, 765)
        dofus_window.moveTo(-8, 0)

import os
from gamewindow import GameWindow
from bot import DofusBot, ImageData


# Variables.
character_name = "Novella"

# Initializing the 'GameWindow()' object.
gamewindow = GameWindow(character_name, official_version=False)

# Initializing 'bot' object
dofusbot = DofusBot(ImageData.amakna_castle_gobballs_images_list, ImageData.amakna_castle_gobballs_images_path, debug_window=True)
#dofusbot = DofusBot(ImageData.test_monster_images_list, ImageData.test_monster_images_path, debug_window=True)


def main():

    if gamewindow.gamewindow_checkifexists() == True:
        gamewindow.gamewindow_resize()
        # Starting the 'bot' thread.
        dofusbot.DofusBot_Thread_start()
    else:
        os._exit(1)


if __name__ == '__main__':
    main()

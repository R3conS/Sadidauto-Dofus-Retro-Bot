import os
from game_window import GameWindow
from bot import DofusBot, ImageData


# Variables.
character_name = "Novella"

# Initializing the 'GameWindow()' object.
gamewindow = GameWindow(character_name, False)

# Initializing 'bot' object
# dofusbot = DofusBot(ImageData.amakna_castle_gobballs_images_list, ImageData.amakna_castle_gobballs_images_path, debug_window=True)
dofusbot = DofusBot(ImageData.test_monster_images_list, ImageData.test_monster_images_path, debug_window=True)


def main():

    if gamewindow.check_if_exists() == True:
        gamewindow.resize_and_move()
        # Starting the 'bot' thread.
        dofusbot.DofusBot_Thread_start()
    else:
        os._exit(1)


if __name__ == '__main__':
    main()

import os
from gamewindow import GameWindow
from bot import DofusBot, ImageData


# Initializing the 'GameWindow()' object.
gamewindow = GameWindow("Novella", "v1.35.1")

# Initializing 'bot' object
dofusbot = DofusBot(ImageData.gobbal_images_list, ImageData.gobbal_images_path, debug_window=True)
#dofus_bot = DofusBot(ImageData.test_monster_images_list, ImageData.test_monster_images_path)


def main():

    if gamewindow.gamewindow_checkifexists() == True:
        gamewindow.gamewindow_resize()
        # Starting the 'bot' thread.
        dofusbot.DofusBot_Thread_start()
    else:
        os._exit(1)


if __name__ == '__main__':
    main()

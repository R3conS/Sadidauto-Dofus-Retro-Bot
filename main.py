import os
from gamewindow import GameWindow
from bot import DofusBot, ImageData


# Initializing 'bot' object
dofusbot = DofusBot(ImageData.gobbal_images_list, ImageData.gobbal_images_path, debug_window=True)
#dofus_bot = DofusBot(ImageData.test_monster_images_list, ImageData.test_monster_images_path)


def main():

    # Initializing the 'GameWindow()' object.
    gamewindow = GameWindow("Novella", "v1.35.1")

    if gamewindow.gamewindow_checkifexists() == True:
        gamewindow.gamewindow_resize()
        # Starting the 'bot' thread.
        print(f"[INFO] Starting 'DofusBot_Thread' ... ")
        dofusbot.DofusBot_Thread_start()
    else:
        os._exit(1)


if __name__ == '__main__':
    main()

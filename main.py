import os

from game_window import GameWindow
from acg_bot import Bot, ImageData


# Variables.
character_name = "Novella"

# Initializing the 'GameWindow()' object.
gamewindow = GameWindow(character_name, False)

# Initializing 'bot' object
bot = Bot(debug_window=True)

# For testing.
# bot = Bot(ImageData.test_monster_images_list, 
#           ImageData.test_monster_images_path, 
#           debug_window=True)


def main():

    if gamewindow.check_if_exists() == True:
        gamewindow.resize_and_move()
        # Starting the 'bot' thread.
        bot.Bot_Thread_start()
    else:
        os._exit(1)


if __name__ == '__main__':
    main()

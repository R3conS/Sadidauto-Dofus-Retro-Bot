from acg_bot import Bot, ImageData


# Initializing 'bot' object
character_name = "Novella"
bot = Bot(character_name=character_name, 
          official_version=False,
          debug_window=True)

# For testing.
# bot = Bot(objects_list=ImageData.test_monster_images_list, 
#           objects_path=ImageData.test_monster_images_path,
#           character_name=character_name,
#           official_version=True,
#           debug_window=True)


def main():
    bot.Bot_Thread_start()


if __name__ == '__main__':
    main()

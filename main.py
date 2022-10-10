from bot import Bot


# Initializing 'bot' object
character_name = "Bobas"
bot = Bot(script="amakna_castle_gobballs",
          character_name=character_name, 
          official_version=False,
          debug_window=True,
          detection_threshold=0.6)

# For testing.
# bot = Bot(script="testing"
#           character_name=character_name,
#           official_version=False,
#           debug_window=True)


def main():
    bot.Bot_Thread_start()


if __name__ == '__main__':
    main()

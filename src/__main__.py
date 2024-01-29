from src.logger import Logger
log = Logger.get_logger()

import os

from pynput import keyboard

from cmd_line_parser import Parser
from src.bot.bot import Bot


def exit_with_hotkey():
    def exit():
        log.info("Exit hotkey '<ctrl>+<alt>+w' pressed! Exiting ... ")
        os._exit(1)
    with keyboard.GlobalHotKeys({"<ctrl>+<alt>+w": exit}) as h:
        h.join()


def main():
    # args = Parser.parse_command_line()
    # bot = Bot(script=args.script, character_name=args.character_name)
    # bot.start()
    bot = Bot(
        script="af_anticlock", 
        character_name="Chick-[AYU]", 
        server_name="Allisteria"
    )
    bot.start()
    exit_with_hotkey()


if __name__ == '__main__':
    main()

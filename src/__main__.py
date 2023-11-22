from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True, True)

import os

from pynput import keyboard

from bot import Bot
from cmd_line_parser import Parser


def exit_with_hotkey():
    def exit():
        log.info("Exit hotkey '<ctrl>+<alt>+q' pressed! Exiting ... ")
        os._exit(1)
    with keyboard.GlobalHotKeys({"<ctrl>+<alt>+q": exit}) as h:
        h.join()


def main():
    # args = Parser.parse_command_line()
    # bot = Bot(script=args.script, character_name=args.character_name)
    # bot.start()
    bot = Bot(script="af_anticlock", character_name="Juni")
    bot.start()
    exit_with_hotkey()


if __name__ == '__main__':
    main()

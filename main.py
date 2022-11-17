from logger import Logger
log = Logger.setup_logger("GLOBAL", Logger.DEBUG, True)

import os

from pynput import keyboard

from bot import Bot
from cmd_line_parser import Parser


def exit_with_hotkey():

    def exit():
        log.info("Exit hotkey '<ctrl>+<alt>+w' pressed!")
        log.info("Exiting ... ")
        os._exit(1)

    with keyboard.GlobalHotKeys({"<ctrl>+<alt>+w": exit}) as h:
        h.join()


def main():

    args = Parser.parse_command_line()
    bot = Bot(script=args.script,
                character_name=args.character_name,
                official_version=args.official_version,
                debug_window=args.debug_window)
    bot.Bot_Thread_start()
    exit_with_hotkey()


if __name__ == '__main__':
    main()

from src.logger import Logger
log = Logger.get_logger()

import os
import sys

from pynput import keyboard

from cmd_line_parser import Parser
from src.bot.bot import Bot
from src.gui.application.application import Application
from src.gui.main_window.main_window import MainWindow


def exit_with_hotkey():
    def exit():
        log.info("Exit hotkey '<ctrl>+<alt>+w' pressed! Exiting ... ")
        os._exit(1)
    with keyboard.GlobalHotKeys({"<ctrl>+<alt>+w": exit}) as h:
        h.join()


def main():
    # args = Parser.parse_command_line()
    # bot = Bot(script=args.script, character_name=args.character_name, server_name=args.server_name)
    # bot.start()
    # exit_with_hotkey()

    # ToDo: add headless mode to parser.
    app = Application(sys.argv)
    main_window = MainWindow(app)
    main_window.show()
    app.exec()


if __name__ == '__main__':
    main()

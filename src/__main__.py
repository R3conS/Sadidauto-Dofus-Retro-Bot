from src.logger import Logger
import logging
# log = Logger.get_logger()

import multiprocessing as mp
import os
import sys

from pynput import keyboard

from cmd_line_parser import Parser
from src.bot.bot import Bot
# from src.gui.application.application import Application
# from src.gui.main_window.main_window import MainWindow
from src.log_listener import LogListener
from datetime import datetime

def exit_with_hotkey():
    def exit():
        # log.info("Exit hotkey '<ctrl>+<alt>+w' pressed! Exiting ... ")
        os._exit(1)
    with keyboard.GlobalHotKeys({"<ctrl>+<alt>+w": exit}) as h:
        h.join()


def create_session_file():
    with open(
        os.path.join(os.getcwd(), datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3] + ".session"),
        "w"
    ) as f:
        print("Session file created!")
        f.write(f"Created in: {__name__}")


def main():
    create_session_file()
    Logger.get_session_file_name()
    Logger.create_session_log_folder()

    log_queue = mp.Queue()

    # Configure main process logger.
    Logger.configure_main_process_logger(log_queue)

    log_listener = LogListener(log_queue)
    log_listener.start()

    log = logging.getLogger()
    log.info("Main process started!")

    bot = Bot(log_queue)
    bot.start()

    # args = Parser.parse_command_line()
    # bot = Bot(
    #     character_name=args.character_name, 
    #     server_name=args.server_name,
    #     script=args.script
    # )
    # bot.start()
    # exit_with_hotkey()

    # # ToDo: add headless mode to parser.
    # app = Application(sys.argv)
    # main_window = MainWindow(app)
    # main_window.show()
    # app.exec()


if __name__ == '__main__':
    main()

from src.logger import get_logger

log = get_logger()

import os
import sys

from pynput import keyboard

from src.gui.application.application import Application
from src.gui.main_window.main_window import MainWindow


def exit_with_hotkey():
    def exit():
        log.info("Exit hotkey '<ctrl>+<alt>+w' pressed! Exiting ... ")
        os._exit(0)
    with keyboard.GlobalHotKeys({"<ctrl>+<alt>+w": exit}) as h:
        h.join()


def main():
    # ToDo: add ability to run bot headless without GUI.
    app = Application(sys.argv)
    main_window = MainWindow(app)
    main_window.show()
    app.exec()


if __name__ == '__main__':
    main()

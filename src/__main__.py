from src.logger import get_logger

log = get_logger()

import sys

from src.gui.application.application import Application
from src.gui.main_window.main_window import MainWindow


def main():
    app = Application(sys.argv)
    main_window = MainWindow(app)
    main_window.show()
    app.exec()


if __name__ == '__main__':
    main()

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow

from src.gui.main_window.MainWindow_ui import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, app: QApplication):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("oFlexBot")
        self.app = app
        self.setFocus()
        self.setFocusPolicy(Qt.ClickFocus)

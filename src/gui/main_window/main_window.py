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
        self.setFocusPolicy(Qt.ClickFocus) # Make all widgets lose focus when clicking on the main window.
        self.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint) # Set non resizable.
        self.character_name_line_edit.setText("Chick-[AYU]")
        self._connect_signals_and_slots()
        self.bot = None

    def _connect_signals_and_slots(self):
        self.start_button.bot_object_initialized_signal.connect(self._on_bot_object_initialized_signal)

    def _on_bot_object_initialized_signal(self, bot_object):
        self.bot = bot_object

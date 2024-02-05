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

    def _connect_signals_and_slots(self):
        self.start_button.bot_started_signal.connect(self.stop_button._on_bot_started)
        self.start_button.bot_exited_due_to_exception_signal.connect(self.stop_button._on_bot_exited_due_to_exception)
        self.stop_button.bot_stopped_signal.connect(self.start_button._on_bot_stopped)

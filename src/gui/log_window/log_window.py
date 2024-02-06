from PySide6.QtWidgets import QWidget

from src.gui.log_window.LogWindow_ui import Ui_LogWindow


class LogWindow(QWidget, Ui_LogWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("oFlexBot - Log Window")
        self._connect_signals_and_slots()

    def _connect_signals_and_slots(self):
        self.clear_console_button.clicked.connect(self.console_plain_text_edit.clear)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = LogWindow()
    window.show()
    sys.exit(app.exec())

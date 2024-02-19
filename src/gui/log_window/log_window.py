from PySide6.QtWidgets import QWidget

from src.gui.log_window.bot_process_log_reader import BotProcessLogReader
from src.gui.log_window.LogWindow_ui import Ui_LogWindow


class LogWindow(QWidget, Ui_LogWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("oFlexBot - Log Window")
        self._connect_signals_and_slots()
        self.fully_close_on_close_event = False

    def _connect_signals_and_slots(self):
        self.clear_console_button.clicked.connect(self.console_plain_text_edit.clear)

    def on_bot_started(self, bot_process, start_time):
        reader = BotProcessLogReader(bot_process, start_time)
        reader.log_file_line_read.connect(self.console_plain_text_edit.on_log_file_line_read)
        reader.start()

    def closeEvent(self, event):
        if not self.fully_close_on_close_event:
            self.hide()
            event.ignore()
        else:
            event.accept()


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = LogWindow()
    window.show()
    sys.exit(app.exec())

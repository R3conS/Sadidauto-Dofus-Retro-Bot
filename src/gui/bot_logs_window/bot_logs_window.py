from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from src.gui.bot_logs_window.bot_process_log_reader import BotProcessLogReader
from src.gui.bot_logs_window.BotLogsWindow_ui import Ui_BotLogsWindow


class BotLogsWindow(QWidget, Ui_BotLogsWindow):

    log_file_line_read = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Sadidauto - Bot Logs")
        self.fully_close_on_close_event = False

    def on_bot_started(self, bot_process, start_time):
        self.bot_logs_plain_text_edit.clear()
        reader = BotProcessLogReader(bot_process, start_time)
        reader.log_file_line_read.connect(self.bot_logs_plain_text_edit.on_log_file_line_read)
        reader.log_file_line_read.connect(lambda line: self.log_file_line_read.emit(line))
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
    window = BotLogsWindow()
    window.show()
    sys.exit(app.exec())

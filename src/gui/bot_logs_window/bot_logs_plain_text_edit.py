from PySide6.QtGui import QFont
from PySide6.QtWidgets import QPlainTextEdit


class BotLogsPlainTextEdit(QPlainTextEdit):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._read_only = True
        self.setFont(QFont("Segoe UI", 10))

    """Override"""
    def setReadOnly(self, _):
        # For some reason using self.setReadOnly() in __init__() doesn't work.
        # Works either through QT Designer or like this.
        return super().setReadOnly(self._read_only)

    def on_log_file_line_read(self, line: str):
        self.appendHtml(line)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

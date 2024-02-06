from datetime import datetime

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QPlainTextEdit


class ConsolePlainTextEdit(QPlainTextEdit):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._read_only = True
        self.setFont(QFont("Arial", 10))  # Set font globally for the widget

    """Override"""
    def setReadOnly(self, _):
        # For some reason using self.setReadOnly() in __init__() doesn't work.
        # Works either through QT Designer or like this.
        return super().setReadOnly(self._read_only)

    def append_text(self, text):
        self.appendHtml(f"<b>[{self._get_time_stamp()}]</b> {text}")
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def _get_time_stamp(self):
        return datetime.now().strftime("%H:%M:%S")

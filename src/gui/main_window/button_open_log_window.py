from PySide6.QtWidgets import QPushButton

from src.gui.log_window.log_window import LogWindow


class OpenLogWindowButton(QPushButton):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.clicked.connect(self._on_clicked)
        self.log_window = None

    def _on_clicked(self):
        if self.log_window is None:
            self.log_window = LogWindow()
        self.log_window.show()

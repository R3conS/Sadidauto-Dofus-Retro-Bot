from PySide6.QtWidgets import QPushButton


class OpenLogWindowButton(QPushButton):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.clicked.connect(self._on_clicked)
        self.main_window = self.window()

    def _on_clicked(self):
        if self.main_window.log_window is None:
            return
        elif self.main_window.log_window.isVisible():
            self.main_window.log_window.hide()
        elif not self.main_window.log_window.isVisible():
            self.main_window.log_window.show()

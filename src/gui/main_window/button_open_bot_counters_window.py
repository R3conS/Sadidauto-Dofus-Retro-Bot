from PySide6.QtWidgets import QPushButton


class OpenBotCountersWindowButton(QPushButton):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.clicked.connect(self._on_clicked)
        self.main_window = self.window()

    def _on_clicked(self):
        if self.main_window.bot_counters_window is None:
            return
        elif self.main_window.bot_counters_window.isVisible():
            self.main_window.bot_counters_window.hide()
        elif not self.main_window.bot_counters_window.isVisible():
            self.main_window.bot_counters_window.show()

from PySide6.QtWidgets import QWidget

from src.gui.bot_counters_window.BotCountersWindow_ui import Ui_BotCountersWindow


class BotCountersWindow(QWidget, Ui_BotCountersWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("oFlexBot - Bot Counters")
        self.fully_close_on_close_event = False

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
    window = BotCountersWindow()
    window.show()
    sys.exit(app.exec())

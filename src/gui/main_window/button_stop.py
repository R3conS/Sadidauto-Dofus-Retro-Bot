from src.logger import get_logger

log = get_logger()

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QPushButton


class StopButton(QPushButton):

    bot_stopped_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.clicked.connect(self._on_clicked)
        self.setEnabled(False)
        self.bot = None

    def _on_clicked(self):
        log.info("Stopping the bot process ...")
        self.bot.stop()
        self.bot.join()
        self.bot_stopped_signal.emit()
        self.setEnabled(False)
        log.info("Bot process has stopped!")

    def on_bot_started(self, bot_object):
        self.bot = bot_object
        self.setEnabled(True)

    def on_bot_exited_due_to_exception(self):
        self.setEnabled(False)

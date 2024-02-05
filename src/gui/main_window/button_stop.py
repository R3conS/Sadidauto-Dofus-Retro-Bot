from src.logger import Logger
log = Logger.get_logger()

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
        log.info("Stopping the bot ...")
        self.bot.stop()
        self.bot.join()
        self.bot_stopped_signal.emit()
        self.setEnabled(False)
        log.info("Bot has stopped!")

    def _on_bot_started(self, bot_object):
        self.bot = bot_object
        self.setEnabled(True)

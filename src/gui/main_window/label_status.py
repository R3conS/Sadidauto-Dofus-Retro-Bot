from PySide6.QtWidgets import QLabel


class StatusLabel(QLabel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("color: yellow")
        # The initial text is set in the .ui file. For some reason
        # calling setText() in the constructor does not work.

    def on_initialization_options_invalid(self, message: str):
        self.setStyleSheet("color: red")
        self.setText(message)

    def on_bot_started(self):
        self.setStyleSheet("color: #61e332;")
        self.setText("Bot is running.")

    def on_bot_stopped(self):
        self.setStyleSheet("color: yellow")
        self.setText("Bot is stopped.")

from PySide6.QtWidgets import QLabel


class StatusLabel(QLabel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("color: yellow")

    def on_initialization_options_invalid(self, message: str):
        self.setStyleSheet("color: red")
        self.setText(message)

from PySide6.QtWidgets import QLabel


class StatusLabel(QLabel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("color: red")

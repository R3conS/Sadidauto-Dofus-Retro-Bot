from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox


class ServerComboBox(QComboBox):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("font-size: 12px;")
        self.setPlaceholderText(" ")
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.lineEdit().setAlignment(Qt.AlignCenter)
        self.addItem("Boune")
        self.addItem("Allisteria")
        self.addItem("Fallanster")
        self.addItem("Semi-like (Abrak)")
        self.currentIndexChanged.connect(lambda: self.clearFocus())

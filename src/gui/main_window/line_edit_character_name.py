from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit


class CharacterNameLineEdit(QLineEdit):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Enter character's name")
        self.setMaxLength(20)
        self.setStyleSheet("font-size: 12px;")
        self.setAlignment(Qt.AlignCenter)

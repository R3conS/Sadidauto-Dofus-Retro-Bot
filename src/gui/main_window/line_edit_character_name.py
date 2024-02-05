from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit


class CharacterNameLineEdit(QLineEdit):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Enter character's name")
        self.setMaxLength(20)
        self.setAlignment(Qt.AlignCenter)
        self.textChanged.connect(self._on_text_changed_singal)

    def _on_text_changed_singal(self):
        # Aligning text properly (centering) with other widgets below.
        # Like combo boxes and spin boxes.
        if self.text() != "":
            self.setStyleSheet("""
                font-size: 12px;
                padding-right: 20px
            """)
            self.setMinimumHeight(24)
        else:
            self.setStyleSheet("""""")
            self.setMinimumHeight(0)

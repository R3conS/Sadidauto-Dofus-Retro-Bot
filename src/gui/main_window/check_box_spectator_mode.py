from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox


class SpectatorModeCheckBox(QCheckBox):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.NoFocus)
        self.setChecked(True)

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSpinBox


class PodsPercentageSpinBox(QSpinBox):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 90)
        self.setValue(90)
        self.setSuffix("%")
        self.setSingleStep(1)
        self.setAlignment(Qt.AlignCenter)
        
import ctypes

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPalette
from PySide6.QtWidgets import QApplication


class Application(QApplication):

    STYLE = "Fusion"
    ICON_PATH = "src\\gui\\application\\logo.png"

    def __init__(self, argv):
        super().__init__(argv)
        self._set_app_id()
        self.setStyle(self.STYLE)
        self.setPalette(self._get_default_palette(self))
        self.setWindowIcon(QIcon(self.ICON_PATH))

    def _set_app_id(self):
        """
        Set AppUserModelID so that the app icon is displayed in the taskbar.
        
        https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105
        """
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Sadidauto.Application")

    def _get_default_palette(self, application: QApplication):
        palette = application.palette()
        palette.setColorGroup(
            QPalette.Active,     # color group
            Qt.white,            # windowText
            QColor(65, 65, 65),  # button
            QColor(95, 95, 95),  # light
            QColor(40, 40, 40),  # dark
            QColor(60, 60, 60),  # mid
            Qt.white,            # text
            Qt.blue,             # bright_text
            QColor(55, 55, 55),  # base
            QColor(40, 40, 40)   # window
        )
        palette.setColorGroup(
            QPalette.Inactive,   # color group
            Qt.white,            # windowText
            QColor(65, 65, 65),  # button
            QColor(95, 95, 95),  # light
            QColor(40, 40, 40),  # dark
            QColor(60, 60, 60),  # mid
            Qt.white,            # text
            Qt.blue,             # bright_text
            QColor(55, 55, 55),  # base
            QColor(40, 40, 40)   # window
        )
        return palette

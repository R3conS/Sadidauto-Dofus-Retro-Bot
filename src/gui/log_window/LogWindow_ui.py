# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'LogWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.6.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QSizePolicy,
    QVBoxLayout, QWidget)

from src.gui.log_window.button_clear_console import ClearConsoleButton
from src.gui.log_window.plain_text_edit_console import ConsolePlainTextEdit

class Ui_LogWindow(object):
    def setupUi(self, LogWindow):
        if not LogWindow.objectName():
            LogWindow.setObjectName(u"LogWindow")
        LogWindow.resize(564, 458)
        self.verticalLayout_2 = QVBoxLayout(LogWindow)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.console_text_edit_frame = QFrame(LogWindow)
        self.console_text_edit_frame.setObjectName(u"console_text_edit_frame")
        self.console_text_edit_frame.setFrameShape(QFrame.NoFrame)
        self.console_text_edit_frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.console_text_edit_frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.console_plain_text_edit = ConsolePlainTextEdit(self.console_text_edit_frame)
        self.console_plain_text_edit.setObjectName(u"console_plain_text_edit")
        self.console_plain_text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.console_plain_text_edit.setReadOnly(False)

        self.verticalLayout.addWidget(self.console_plain_text_edit)


        self.verticalLayout_2.addWidget(self.console_text_edit_frame)

        self.frame = QFrame(LogWindow)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.clear_console_button = ClearConsoleButton(self.frame)
        self.clear_console_button.setObjectName(u"clear_console_button")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.clear_console_button.sizePolicy().hasHeightForWidth())
        self.clear_console_button.setSizePolicy(sizePolicy)
        self.clear_console_button.setMinimumSize(QSize(100, 0))

        self.horizontalLayout.addWidget(self.clear_console_button)


        self.verticalLayout_2.addWidget(self.frame)


        self.retranslateUi(LogWindow)

        QMetaObject.connectSlotsByName(LogWindow)
    # setupUi

    def retranslateUi(self, LogWindow):
        LogWindow.setWindowTitle(QCoreApplication.translate("LogWindow", u"LogWindow", None))
        self.clear_console_button.setText(QCoreApplication.translate("LogWindow", u"Clear Console", None))
    # retranslateUi


# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'BotLogsWindow.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QSizePolicy, QVBoxLayout,
    QWidget)

from src.gui.bot_logs_window.bot_logs_plain_text_edit import BotLogsPlainTextEdit

class Ui_BotLogsWindow(object):
    def setupUi(self, BotLogsWindow):
        if not BotLogsWindow.objectName():
            BotLogsWindow.setObjectName(u"BotLogsWindow")
        BotLogsWindow.resize(619, 398)
        self.verticalLayout_3 = QVBoxLayout(BotLogsWindow)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.frame_1 = QFrame(BotLogsWindow)
        self.frame_1.setObjectName(u"frame_1")
        self.frame_1.setFrameShape(QFrame.NoFrame)
        self.frame_1.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.frame_1)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.bot_logs_plain_text_edit = BotLogsPlainTextEdit(self.frame_1)
        self.bot_logs_plain_text_edit.setObjectName(u"bot_logs_plain_text_edit")
        self.bot_logs_plain_text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.bot_logs_plain_text_edit.setReadOnly(False)

        self.verticalLayout.addWidget(self.bot_logs_plain_text_edit)


        self.verticalLayout_3.addWidget(self.frame_1)

        self.verticalLayout_3.setStretch(0, 6)

        self.retranslateUi(BotLogsWindow)

        QMetaObject.connectSlotsByName(BotLogsWindow)
    # setupUi

    def retranslateUi(self, BotLogsWindow):
        BotLogsWindow.setWindowTitle(QCoreApplication.translate("BotLogsWindow", u"BotLogsWindow", None))
    # retranslateUi


# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'BotCountersWindow.ui'
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

from src.gui.bot_counters_window.bot_counters_plain_text_edit import BotCountersPlainTextEdit

class Ui_BotCountersWindow(object):
    def setupUi(self, BotCountersWindow):
        if not BotCountersWindow.objectName():
            BotCountersWindow.setObjectName(u"BotCountersWindow")
        BotCountersWindow.resize(300, 200)
        self.verticalLayout_3 = QVBoxLayout(BotCountersWindow)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.frame_1 = QFrame(BotCountersWindow)
        self.frame_1.setObjectName(u"frame_1")
        self.frame_1.setFrameShape(QFrame.NoFrame)
        self.frame_1.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.frame_1)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.bot_counters_plain_text_edit = BotCountersPlainTextEdit(self.frame_1)
        self.bot_counters_plain_text_edit.setObjectName(u"bot_counters_plain_text_edit")
        self.bot_counters_plain_text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.bot_counters_plain_text_edit.setReadOnly(False)

        self.verticalLayout.addWidget(self.bot_counters_plain_text_edit)


        self.verticalLayout_3.addWidget(self.frame_1)

        self.verticalLayout_3.setStretch(0, 6)

        self.retranslateUi(BotCountersWindow)

        QMetaObject.connectSlotsByName(BotCountersWindow)
    # setupUi

    def retranslateUi(self, BotCountersWindow):
        BotCountersWindow.setWindowTitle(QCoreApplication.translate("BotCountersWindow", u"BotCountersWindow", None))
    # retranslateUi


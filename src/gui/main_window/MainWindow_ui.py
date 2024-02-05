# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainWindow.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QMainWindow, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

from src.gui.main_window.check_box_spectator_mode import SpectatorModeCheckBox
from src.gui.main_window.combo_box_script import ScriptComboBox
from src.gui.main_window.combo_box_server import ServerComboBox
from src.gui.main_window.line_edit_character_name import CharacterNameLineEdit
from src.gui.main_window.spin_box_pods_percentage import PodsPercentageSpinBox

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(429, 338)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(429, 338))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_5 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(-1, 10, -1, -1)
        self.capture_duration_label = QLabel(self.centralwidget)
        self.capture_duration_label.setObjectName(u"capture_duration_label")
        font = QFont()
        font.setPointSize(32)
        font.setBold(True)
        self.capture_duration_label.setFont(font)

        self.horizontalLayout_9.addWidget(self.capture_duration_label, 0, Qt.AlignHCenter|Qt.AlignVCenter)


        self.verticalLayout_2.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(-1, 10, -1, 10)
        self.line_2 = QFrame(self.centralwidget)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShadow(QFrame.Sunken)
        self.line_2.setLineWidth(2)
        self.line_2.setFrameShape(QFrame.HLine)

        self.horizontalLayout_8.addWidget(self.line_2)


        self.verticalLayout_2.addLayout(self.horizontalLayout_8)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)
        font1 = QFont()
        font1.setPointSize(12)
        font1.setBold(False)
        self.label.setFont(font1)

        self.horizontalLayout.addWidget(self.label)

        self.character_name_line_edit = CharacterNameLineEdit(self.centralwidget)
        self.character_name_line_edit.setObjectName(u"character_name_line_edit")
        sizePolicy1.setHeightForWidth(self.character_name_line_edit.sizePolicy().hasHeightForWidth())
        self.character_name_line_edit.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.character_name_line_edit)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_14 = QLabel(self.centralwidget)
        self.label_14.setObjectName(u"label_14")
        sizePolicy1.setHeightForWidth(self.label_14.sizePolicy().hasHeightForWidth())
        self.label_14.setSizePolicy(sizePolicy1)
        self.label_14.setFont(font1)

        self.horizontalLayout_3.addWidget(self.label_14)

        self.server_combo_box = ServerComboBox(self.centralwidget)
        self.server_combo_box.setObjectName(u"server_combo_box")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.server_combo_box.sizePolicy().hasHeightForWidth())
        self.server_combo_box.setSizePolicy(sizePolicy2)

        self.horizontalLayout_3.addWidget(self.server_combo_box)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_15 = QLabel(self.centralwidget)
        self.label_15.setObjectName(u"label_15")
        sizePolicy1.setHeightForWidth(self.label_15.sizePolicy().hasHeightForWidth())
        self.label_15.setSizePolicy(sizePolicy1)
        self.label_15.setFont(font1)

        self.horizontalLayout_4.addWidget(self.label_15)

        self.script_combo_box = ScriptComboBox(self.centralwidget)
        self.script_combo_box.setObjectName(u"script_combo_box")
        sizePolicy2.setHeightForWidth(self.script_combo_box.sizePolicy().hasHeightForWidth())
        self.script_combo_box.setSizePolicy(sizePolicy2)

        self.horizontalLayout_4.addWidget(self.script_combo_box)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_16 = QLabel(self.centralwidget)
        self.label_16.setObjectName(u"label_16")
        sizePolicy1.setHeightForWidth(self.label_16.sizePolicy().hasHeightForWidth())
        self.label_16.setSizePolicy(sizePolicy1)
        self.label_16.setFont(font1)

        self.horizontalLayout_5.addWidget(self.label_16)

        self.bank_percentage_spin_box = PodsPercentageSpinBox(self.centralwidget)
        self.bank_percentage_spin_box.setObjectName(u"bank_percentage_spin_box")
        sizePolicy2.setHeightForWidth(self.bank_percentage_spin_box.sizePolicy().hasHeightForWidth())
        self.bank_percentage_spin_box.setSizePolicy(sizePolicy2)

        self.horizontalLayout_5.addWidget(self.bank_percentage_spin_box)


        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        sizePolicy1.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy1)
        self.label_2.setFont(font1)

        self.horizontalLayout_6.addWidget(self.label_2)

        self.spectator_mode_check_box = SpectatorModeCheckBox(self.centralwidget)
        self.spectator_mode_check_box.setObjectName(u"spectator_mode_check_box")
        sizePolicy2.setHeightForWidth(self.spectator_mode_check_box.sizePolicy().hasHeightForWidth())
        self.spectator_mode_check_box.setSizePolicy(sizePolicy2)

        self.horizontalLayout_6.addWidget(self.spectator_mode_check_box)


        self.verticalLayout.addLayout(self.horizontalLayout_6)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(-1, 10, -1, 10)
        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShadow(QFrame.Sunken)
        self.line.setLineWidth(2)
        self.line.setFrameShape(QFrame.HLine)

        self.horizontalLayout_7.addWidget(self.line)


        self.verticalLayout_2.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(-1, -1, -1, 10)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.pushButton = QPushButton(self.centralwidget)
        self.pushButton.setObjectName(u"pushButton")

        self.horizontalLayout_2.addWidget(self.pushButton)

        self.pushButton_3 = QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName(u"pushButton_3")

        self.horizontalLayout_2.addWidget(self.pushButton_3)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)


        self.verticalLayout_5.addLayout(self.verticalLayout_2)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.capture_duration_label.setText(QCoreApplication.translate("MainWindow", u"00:00", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Character Name", None))
        self.character_name_line_edit.setText("")
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"Server", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"Script", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"Return to bank at pods %", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Disable spectator mode?", None))
        self.spectator_mode_check_box.setText("")
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
    # retranslateUi


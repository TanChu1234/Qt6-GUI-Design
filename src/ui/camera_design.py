# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'camera.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QListView,
    QListWidget, QListWidgetItem, QPushButton, QSizePolicy,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1780, 820)
        Form.setMinimumSize(QSize(1390, 0))
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        Form.setFont(font)
        Form.setStyleSheet(u"/* Main Window Background */\n"
"QWidget {\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, \n"
"                                stop:0 #1E1E2E, stop:1 #252836);\n"
"    color: white;\n"
"    font-size: 14px;\n"
"    font-family: \"Segoe UI\", sans-serif;\n"
"}\n"
"\n"
"/* Unified Button Style */\n"
"QPushButton {\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, \n"
"                                stop:0 #007AFF, stop:1 #009FFF);\n"
"    border: none;\n"
"    padding: 12px 20px;\n"
"    font-size: 14px;\n"
"    font-weight: bold;\n"
"    border-radius: 5px;\n"
"	min-width: 50px;\n"
"    color: white;\n"
"    text-align: center;\n"
"}\n"
"\n"
"/* Button Hover Effect */\n"
"QPushButton:hover {\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, \n"
"                                stop:0 #66BFFF, stop:1 #80D5FF);\n"
"}\n"
"\n"
"/* Button Pressed Effect */\n"
"QPushButton:pressed {\n"
"    background-color: rgba(255, 255, 255, 0.2);\n"
"}\n"
"\n"
""
                        "/* Labels */\n"
"QLabel {\n"
"    font-size: 16px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"/* Camera Display */\n"
"QLabel#label {\n"
"    background-color: #FFFFFF;\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"/* Log Label */\n"
"QLabel#label_2 {\n"
"    font-size: 14px;\n"
"    font-weight: bold;\n"
"    color: #FFFFFF;\n"
"}\n"
"\n"
"/* List Widgets */\n"
"QListWidget#listWidget {\n"
"    background-color: rgb(255, 255, 255);\n"
"    border-radius: 5px;\n"
"    padding: 5px;\n"
"    color: black;\n"
"    font-size: 14px;\n"
"}\n"
"QListWidget#log_list {\n"
"    background-color: rgb(255, 255, 255);\n"
"	border-radius:5px;\n"
"    padding: 5px;\n"
"    color: black;\n"
"    font-size: 11px;\n"
"}")
        self.layoutWidget = QWidget(Form)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(0, 0, 1761, 800))
        self.gridLayout = QGridLayout(self.layoutWidget)
        self.gridLayout.setSpacing(10)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 2, 0, 0)
        self.log_list = QListWidget(self.layoutWidget)
        self.log_list.setObjectName(u"log_list")
        self.log_list.setMinimumSize(QSize(0, 60))
        self.log_list.setStyleSheet(u"")

        self.gridLayout.addWidget(self.log_list, 4, 8, 5, 1)

        self.label_2 = QLabel(self.layoutWidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(50, 40))
        font1 = QFont()
        font1.setFamilies([u"Segoe UI"])
        font1.setBold(True)
        self.label_2.setFont(font1)
        self.label_2.setStyleSheet(u"	border: 1px solid rgb(255, 255, 255);\n"
"	border-radius:5px;")
        self.label_2.setAlignment(Qt.AlignCenter)
        self.label_2.setIndent(0)

        self.gridLayout.addWidget(self.label_2, 9, 8, 1, 1)

        self.label = QLabel(self.layoutWidget)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(1080, 720))
        self.label.setMaximumSize(QSize(1080, 16777215))
        self.label.setSizeIncrement(QSize(0, 0))
        self.label.setStyleSheet(u"")
        self.label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.label, 4, 1, 5, 7)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setHorizontalSpacing(8)
        self.gridLayout_2.setVerticalSpacing(0)
        self.add_cam = QPushButton(self.layoutWidget)
        self.add_cam.setObjectName(u"add_cam")
        self.add_cam.setMinimumSize(QSize(90, 60))
        self.add_cam.setFont(font1)
        self.add_cam.setStyleSheet(u"")

        self.gridLayout_2.addWidget(self.add_cam, 0, 0, 1, 1)

        self.remove_cam = QPushButton(self.layoutWidget)
        self.remove_cam.setObjectName(u"remove_cam")
        self.remove_cam.setMinimumSize(QSize(90, 60))
        self.remove_cam.setFont(font1)
        self.remove_cam.setStyleSheet(u"")

        self.gridLayout_2.addWidget(self.remove_cam, 0, 1, 1, 1)


        self.gridLayout.addLayout(self.gridLayout_2, 9, 0, 1, 1)

        self.listWidget = QListWidget(self.layoutWidget)
        font2 = QFont()
        font2.setPointSize(14)
        font2.setBold(True)
        __qlistwidgetitem = QListWidgetItem(self.listWidget)
        __qlistwidgetitem.setFont(font2);
        self.listWidget.setObjectName(u"listWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget.sizePolicy().hasHeightForWidth())
        self.listWidget.setSizePolicy(sizePolicy)
        self.listWidget.setMinimumSize(QSize(296, 0))
        self.listWidget.setSizeIncrement(QSize(0, 0))
        self.listWidget.setFont(font)
        self.listWidget.setFlow(QListView.TopToBottom)

        self.gridLayout.addWidget(self.listWidget, 4, 0, 5, 1)

        self.connect = QPushButton(self.layoutWidget)
        self.connect.setObjectName(u"connect")
        self.connect.setMinimumSize(QSize(90, 60))
        self.connect.setMaximumSize(QSize(16777215, 16777215))
        self.connect.setFont(font1)
        self.connect.setStyleSheet(u"")

        self.gridLayout.addWidget(self.connect, 9, 1, 1, 1)

        self.disconnect = QPushButton(self.layoutWidget)
        self.disconnect.setObjectName(u"disconnect")
        self.disconnect.setMinimumSize(QSize(90, 60))
        self.disconnect.setMaximumSize(QSize(16777215, 16777215))
        self.disconnect.setFont(font1)
        self.disconnect.setStyleSheet(u"")

        self.gridLayout.addWidget(self.disconnect, 9, 2, 1, 1)

        self.trigger = QPushButton(self.layoutWidget)
        self.trigger.setObjectName(u"trigger")
        self.trigger.setMinimumSize(QSize(90, 60))
        self.trigger.setMaximumSize(QSize(16777215, 16777215))
        self.trigger.setFont(font1)
        self.trigger.setStyleSheet(u"")

        self.gridLayout.addWidget(self.trigger, 9, 4, 1, 1)

        self.detect = QPushButton(self.layoutWidget)
        self.detect.setObjectName(u"detect")
        self.detect.setMinimumSize(QSize(90, 60))
        self.detect.setFont(font1)
        self.detect.setStyleSheet(u"")

        self.gridLayout.addWidget(self.detect, 9, 6, 1, 1)

        self.stop_all = QPushButton(self.layoutWidget)
        self.stop_all.setObjectName(u"stop_all")
        self.stop_all.setMinimumSize(QSize(90, 60))
        self.stop_all.setFont(font1)
        self.stop_all.setStyleSheet(u"")

        self.gridLayout.addWidget(self.stop_all, 9, 3, 1, 1)

        self.display = QPushButton(self.layoutWidget)
        self.display.setObjectName(u"display")
        self.display.setMinimumSize(QSize(90, 60))
        self.display.setMaximumSize(QSize(16777215, 16777215))
        self.display.setFont(font1)
        self.display.setStyleSheet(u"")

        self.gridLayout.addWidget(self.display, 9, 5, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"LOG:", None))
        self.label.setText("")
        self.add_cam.setText(QCoreApplication.translate("Form", u"ADD CAM", None))
        self.remove_cam.setText(QCoreApplication.translate("Form", u"DEL CAM", None))

        __sortingEnabled = self.listWidget.isSortingEnabled()
        self.listWidget.setSortingEnabled(False)
        ___qlistwidgetitem = self.listWidget.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("Form", u"Camera ", None));
        self.listWidget.setSortingEnabled(__sortingEnabled)

        self.connect.setText(QCoreApplication.translate("Form", u"CONNECT", None))
        self.disconnect.setText(QCoreApplication.translate("Form", u"DISCONNECT", None))
        self.trigger.setText(QCoreApplication.translate("Form", u"TRIGGER", None))
        self.detect.setText(QCoreApplication.translate("Form", u"DETECT", None))
        self.stop_all.setText(QCoreApplication.translate("Form", u"STOP ALL", None))
        self.display.setText(QCoreApplication.translate("Form", u"DISPLAY", None))
    # retranslateUi


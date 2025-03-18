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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QListView, QListWidget, QListWidgetItem,
    QPushButton, QSizePolicy, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1390, 837)
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
"    color: white;\n"
"    min-width: 70px;\n"
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
"    background-color: rgb(238, 238, 238);\n"
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
"    border-radius: 5px;\n"
"    padding: 5px;\n"
"    color: black;\n"
"    font-size: 9px;\n"
"}")
        self.layoutWidget = QWidget(Form)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(0, 0, 1380, 826))
        self.gridLayout = QGridLayout(self.layoutWidget)
        self.gridLayout.setSpacing(8)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 2, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.start_cam = QPushButton(self.layoutWidget)
        self.start_cam.setObjectName(u"start_cam")
        self.start_cam.setMinimumSize(QSize(123, 60))
        font1 = QFont()
        font1.setFamilies([u"Segoe UI"])
        font1.setBold(True)
        self.start_cam.setFont(font1)

        self.horizontalLayout.addWidget(self.start_cam)

        self.stop_cam = QPushButton(self.layoutWidget)
        self.stop_cam.setObjectName(u"stop_cam")
        self.stop_cam.setMinimumSize(QSize(123, 60))
        self.stop_cam.setFont(font1)

        self.horizontalLayout.addWidget(self.stop_cam)

        self.display = QPushButton(self.layoutWidget)
        self.display.setObjectName(u"display")
        self.display.setMinimumSize(QSize(123, 60))
        self.display.setFont(font1)

        self.horizontalLayout.addWidget(self.display)

        self.run_once = QPushButton(self.layoutWidget)
        self.run_once.setObjectName(u"run_once")
        self.run_once.setMinimumSize(QSize(123, 60))
        self.run_once.setFont(font1)

        self.horizontalLayout.addWidget(self.run_once)

        self.run_continuous = QPushButton(self.layoutWidget)
        self.run_continuous.setObjectName(u"run_continuous")
        self.run_continuous.setMinimumSize(QSize(123, 60))
        self.run_continuous.setFont(font1)

        self.horizontalLayout.addWidget(self.run_continuous)


        self.gridLayout.addLayout(self.horizontalLayout, 10, 1, 1, 1)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setHorizontalSpacing(8)
        self.gridLayout_2.setVerticalSpacing(0)
        self.add_cam = QPushButton(self.layoutWidget)
        self.add_cam.setObjectName(u"add_cam")
        self.add_cam.setMinimumSize(QSize(110, 60))
        self.add_cam.setFont(font1)

        self.gridLayout_2.addWidget(self.add_cam, 0, 0, 1, 1)

        self.remove_cam = QPushButton(self.layoutWidget)
        self.remove_cam.setObjectName(u"remove_cam")
        self.remove_cam.setMinimumSize(QSize(110, 60))
        self.remove_cam.setFont(font1)

        self.gridLayout_2.addWidget(self.remove_cam, 0, 1, 1, 1)


        self.gridLayout.addLayout(self.gridLayout_2, 10, 0, 1, 1)

        self.log_list = QListWidget(self.layoutWidget)
        self.log_list.setObjectName(u"log_list")
        self.log_list.setMinimumSize(QSize(0, 60))

        self.gridLayout.addWidget(self.log_list, 10, 3, 1, 10)

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
        self.listWidget.setMinimumSize(QSize(200, 0))
        self.listWidget.setSizeIncrement(QSize(0, 0))
        self.listWidget.setFont(font)
        self.listWidget.setFlow(QListView.TopToBottom)

        self.gridLayout.addWidget(self.listWidget, 4, 0, 5, 1)

        self.label_2 = QLabel(self.layoutWidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(50, 60))
        self.label_2.setFont(font1)
        self.label_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_2.setIndent(5)

        self.gridLayout.addWidget(self.label_2, 10, 2, 1, 1)

        self.label = QLabel(self.layoutWidget)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(1080, 720))
        self.label.setSizeIncrement(QSize(0, 0))
        self.label.setStyleSheet(u"")
        self.label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.label, 4, 1, 5, 12)

        self.lineEdit = QLineEdit(self.layoutWidget)
        self.lineEdit.setObjectName(u"lineEdit")

        self.gridLayout.addWidget(self.lineEdit, 9, 1, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.start_cam.setText(QCoreApplication.translate("Form", u"START", None))
        self.stop_cam.setText(QCoreApplication.translate("Form", u"STOP", None))
        self.display.setText(QCoreApplication.translate("Form", u"DISPLAY", None))
        self.run_once.setText(QCoreApplication.translate("Form", u"RUN AI \n"
"ONCE TIME", None))
        self.run_continuous.setText(QCoreApplication.translate("Form", u"RUN AI \n"
"REAL TIME", None))
        self.add_cam.setText(QCoreApplication.translate("Form", u"ADD CAM", None))
        self.remove_cam.setText(QCoreApplication.translate("Form", u"DEL CAM", None))

        __sortingEnabled = self.listWidget.isSortingEnabled()
        self.listWidget.setSortingEnabled(False)
        ___qlistwidgetitem = self.listWidget.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("Form", u"Camera ", None));
        self.listWidget.setSortingEnabled(__sortingEnabled)

        self.label_2.setText(QCoreApplication.translate("Form", u"LOG:", None))
        self.label.setText("")
    # retranslateUi


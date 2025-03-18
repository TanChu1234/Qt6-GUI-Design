# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tcp.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QPushButton,
    QSizePolicy, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1415, 733)
        Form.setMinimumSize(QSize(1390, 0))
        Form.setStyleSheet(u"/* Main Window Background */\n"
"QWidget {\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, \n"
"                                stop:0 #1E1E2E, stop:1 #252836);\n"
"    color: white;\n"
"    font-size: 14px;\n"
"    font-family: \"Arial\", sans-serif;\n"
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
        self.layoutWidget.setGeometry(QRect(10, 0, 1371, 723))
        self.gridLayout = QGridLayout(self.layoutWidget)
        self.gridLayout.setSpacing(8)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 2, 0, 0)
        self.log_list_2 = QListWidget(self.layoutWidget)
        self.log_list_2.setObjectName(u"log_list_2")
        self.log_list_2.setMinimumSize(QSize(1080, 720))

        self.gridLayout.addWidget(self.log_list_2, 4, 1, 7, 1)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setHorizontalSpacing(8)
        self.gridLayout_2.setVerticalSpacing(0)
        self.remove_cam = QPushButton(self.layoutWidget)
        self.remove_cam.setObjectName(u"remove_cam")
        self.remove_cam.setMinimumSize(QSize(110, 60))
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setBold(True)
        self.remove_cam.setFont(font)

        self.gridLayout_2.addWidget(self.remove_cam, 1, 1, 1, 1)

        self.add_cam = QPushButton(self.layoutWidget)
        self.add_cam.setObjectName(u"add_cam")
        self.add_cam.setMinimumSize(QSize(110, 60))
        self.add_cam.setFont(font)

        self.gridLayout_2.addWidget(self.add_cam, 0, 1, 1, 1)


        self.gridLayout.addLayout(self.gridLayout_2, 10, 0, 1, 1)

        self.comboBox = QComboBox(self.layoutWidget)
        self.comboBox.setObjectName(u"comboBox")

        self.gridLayout.addWidget(self.comboBox, 4, 0, 1, 1)

        self.label_3 = QLabel(self.layoutWidget)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 5, 0, 1, 1)

        self.lineEdit = QLineEdit(self.layoutWidget)
        self.lineEdit.setObjectName(u"lineEdit")

        self.gridLayout.addWidget(self.lineEdit, 6, 0, 1, 1)

        self.label_4 = QLabel(self.layoutWidget)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 7, 0, 1, 1)

        self.lineEdit_2 = QLineEdit(self.layoutWidget)
        self.lineEdit_2.setObjectName(u"lineEdit_2")

        self.gridLayout.addWidget(self.lineEdit_2, 8, 0, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.remove_cam.setText(QCoreApplication.translate("Form", u"DEL CAM", None))
        self.add_cam.setText(QCoreApplication.translate("Form", u"ADD CAM", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"Adress:", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"Port:", None))
    # retranslateUi


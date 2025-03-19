# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'camera_information.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect, QSize)
from PySide6.QtWidgets import (QComboBox, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget)
from PySide6.QtGui import QFont

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(319, 400)
        Form.setStyleSheet(u"/* Unified Button Style */\n"
"QPushButton {\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, \n"
"                                stop:0 #007AFF, stop:1 #009FFF);\n"
"    border: none;\n"
"    font-weight: bold;\n"
"    border-radius: 5px;\n"
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
"/* LineEdit Style */\n"
"QLineEdit {\n"
"    border: 1px solid #CCCCCC;\n"
"    border-radius: 4px;\n"
"    padding: 4px;\n"
"	color: rgb(0, 0, 0);\n"
"    background-color: #FFFFFF;\n"
"}\n"
"\n"
"QLineEdit:focus {\n"
"    border: 1px solid #007AFF;\n"
"    background-color: #F0F8FF;\n"
"}\n"
"\n"
"/* ComboBox Style */\n"
"QComboBox {\n"
"    border: 1px solid #CCC"
                        "CCC;\n"
"    border-radius: 4px;\n"
"    padding: 4px;\n"
"	color: black;\n"
"    background-color: #FFFFFF;\n"
"}\n"
"\n"
"QComboBox:hover {\n"
"    border: 1px solid #AAAAAA;\n"
"}\n"
"\n"
"QComboBox:focus {\n"
"    border: 1px solid #007AFF;\n"
"}\n"
"\n"
"QComboBox::drop-down {\n"
"    subcontrol-origin: padding;\n"
"    subcontrol-position: top right;\n"
"    width: 20px;\n"
"    border-left: 1px solid #CCCCCC;\n"
"}\n"
"\n"
"QComboBox::down-arrow {\n"
"    image: url(src/asset/images/arrow-down.png);  /* You'll need to provide this image or use a different styling */\n"
"    width: 12px;\n"
"    height: 12px;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"    border: 1px solid #CCCCCC;\n"
"    selection-background-color: #007AFF;\n"
"    selection-color: #FFFFFF;\n"
"}\n"
"\n"
"/* Camera Display */\n"
"QLabel {\n"
"    background-color: none;\n"
"}")
        self.layoutWidget = QWidget(Form)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(20, 30, 281, 275))
        self.gridLayout_2 = QGridLayout(self.layoutWidget)
        self.gridLayout_2.setSpacing(15)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_14 = QLabel(self.layoutWidget)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setMinimumSize(QSize(100, 0))
        font = QFont()
        font.setPointSize(12)
        self.label_14.setFont(font)

        self.gridLayout_2.addWidget(self.label_14, 6, 0, 1, 1)

        self.label_7 = QLabel(self.layoutWidget)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setMinimumSize(QSize(100, 0))
        self.label_7.setFont(font)

        self.gridLayout_2.addWidget(self.label_7, 3, 0, 1, 1)

        self.label_13 = QLabel(self.layoutWidget)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setMinimumSize(QSize(100, 0))
        self.label_13.setFont(font)

        self.gridLayout_2.addWidget(self.label_13, 4, 0, 1, 1)

        self.cam_ip = QLineEdit(self.layoutWidget)
        self.cam_ip.setObjectName(u"cam_ip")
        self.cam_ip.setFont(font)

        self.gridLayout_2.addWidget(self.cam_ip, 1, 1, 1, 1)

        self.comboBox = QComboBox(self.layoutWidget)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setFont(font)

        self.gridLayout_2.addWidget(self.comboBox, 6, 1, 1, 1)

        self.cam_pass = QLineEdit(self.layoutWidget)
        self.cam_pass.setObjectName(u"cam_pass")
        self.cam_pass.setFont(font)

        self.gridLayout_2.addWidget(self.cam_pass, 4, 1, 1, 1)

        self.label = QLabel(self.layoutWidget)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(100, 0))
        self.label.setFont(font)

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.cam_port = QLineEdit(self.layoutWidget)
        self.cam_port.setObjectName(u"cam_port")
        self.cam_port.setFont(font)

        self.gridLayout_2.addWidget(self.cam_port, 2, 1, 1, 1)

        self.cam_user = QLineEdit(self.layoutWidget)
        self.cam_user.setObjectName(u"cam_user")
        self.cam_user.setFont(font)

        self.gridLayout_2.addWidget(self.cam_user, 3, 1, 1, 1)

        self.label_3 = QLabel(self.layoutWidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(100, 0))
        self.label_3.setFont(font)

        self.gridLayout_2.addWidget(self.label_3, 1, 0, 1, 1)

        self.cam_name = QLineEdit(self.layoutWidget)
        self.cam_name.setObjectName(u"cam_name")
        self.cam_name.setFont(font)

        self.gridLayout_2.addWidget(self.cam_name, 0, 1, 1, 1)

        self.label_2 = QLabel(self.layoutWidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(100, 0))
        self.label_2.setFont(font)

        self.gridLayout_2.addWidget(self.label_2, 2, 0, 1, 1)

        self.layoutWidget2 = QWidget(Form)
        self.layoutWidget2.setObjectName(u"layoutWidget2")
        self.layoutWidget2.setGeometry(QRect(70, 340, 191, 42))
        self.horizontalLayout = QHBoxLayout(self.layoutWidget2)
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.ok_button = QPushButton(self.layoutWidget2)
        self.ok_button.setObjectName(u"ok_button")
        self.ok_button.setMinimumSize(QSize(0, 35))
        font1 = QFont()
        font1.setPointSize(12)
        font1.setBold(True)
        self.ok_button.setFont(font1)

        self.horizontalLayout.addWidget(self.ok_button)

        self.cancel_button = QPushButton(self.layoutWidget2)
        self.cancel_button.setObjectName(u"cancel_button")
        self.cancel_button.setMinimumSize(QSize(0, 35))
        self.cancel_button.setBaseSize(QSize(0, 0))
        self.cancel_button.setFont(font1)

        self.horizontalLayout.addWidget(self.cancel_button)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Add Camera", None))
        self.label_14.setText(QCoreApplication.translate("Form", u"Protocols", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"User name:", None))
        self.label_13.setText(QCoreApplication.translate("Form", u"Password:", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("Form", u"RTSP", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("Form", u"HTTP", None))

        self.label.setText(QCoreApplication.translate("Form", u"Camera Name:", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"IP Adress:", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Port:", None))
        self.ok_button.setText(QCoreApplication.translate("Form", u"OK", None))
        self.cancel_button.setText(QCoreApplication.translate("Form", u"Cancel", None))
    # retranslateUi


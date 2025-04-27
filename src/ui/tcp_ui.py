# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tcp_ui.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QListWidget, QListWidgetItem,
    QPushButton, QSizePolicy, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1640, 850)
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
"\n"
"QListWidget#log_list {\n"
"    background-color: rgb(255, 255, 255);\n"
"    border-radius: 5px;\n"
"    padding: 5px;\n"
"    color: black;\n"
"    font-size: 9px;\n"
"}\n"
"\n"
"/* Combo Box Styling */\n"
"QComboBox {\n"
"    background-color: #2E2F3A;\n"
"    border: 1px solid #007AFF;\n"
"    border-radius: 5px;\n"
"    padding: 5px 10px;\n"
"    color: white;\n"
"    font-size: 14px;\n"
"}\n"
"\n"
"QComboBox:hover {\n"
"    border: 1px solid #66BFFF;\n"
"}\n"
""
                        "\n"
"QComboBox QAbstractItemView {\n"
"    background-color: #2E2F3A;\n"
"    border: 1px solid #007AFF;\n"
"    selection-background-color: #007AFF;\n"
"    color: white;\n"
"}\n"
"")
        self.gridLayoutWidget = QWidget(Form)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(0, 0, 731, 601))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.stop_socket = QPushButton(self.gridLayoutWidget)
        self.stop_socket.setObjectName(u"stop_socket")

        self.gridLayout.addWidget(self.stop_socket, 1, 0, 1, 1)

        self.start_socket = QPushButton(self.gridLayoutWidget)
        self.start_socket.setObjectName(u"start_socket")

        self.gridLayout.addWidget(self.start_socket, 0, 0, 1, 1)

        self.listWidget = QListWidget(self.gridLayoutWidget)
        self.listWidget.setObjectName(u"listWidget")

        self.gridLayout.addWidget(self.listWidget, 2, 0, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.stop_socket.setText(QCoreApplication.translate("Form", u"STOP SERVER", None))
        self.start_socket.setText(QCoreApplication.translate("Form", u"START SERVER", None))
    # retranslateUi


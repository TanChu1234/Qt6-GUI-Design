# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QMainWindow, QPushButton,
    QSizePolicy, QStackedWidget, QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1920, 1080)
        MainWindow.setStyleSheet(u"/* Main Window Background */\n"
"QMainWindow {\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, \n"
"                                stop:0 #1E1E2E, stop:1 #252836);\n"
"}\n"
"\n"
"/* General Button Styling */\n"
"QPushButton {\n"
"	background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, \n"
"                                stop:0 #007AFF, stop:1 #009FFF);\n"
"    border: none;\n"
"    padding: 12px 20px;\n"
"    font-size: 24px;\n"
"    font-weight: bold;\n"
"    border-radius: 5px;\n"
"    color: white;\n"
"    min-width: 150px;\n"
"    text-align: left;\n"
"    padding-left: 10px;\n"
"}\n"
"\n"
"/* Button Hover Effect */\n"
"QPushButton:hover {\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, \n"
"                                stop:0 #66BFFF, stop:1 #80D5FF);\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, \n"
"                                stop:0 #027055, stop:1 #00987A);\n"
"}\n"
"")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.camera_page = QPushButton(self.centralwidget)
        self.camera_page.setObjectName(u"camera_page")
        self.camera_page.setGeometry(QRect(40, 30, 211, 80))
        self.camera_page.setMinimumSize(QSize(180, 80))
        self.camera_page.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.camera_page.setLayoutDirection(Qt.LeftToRight)
        icon = QIcon()
        icon.addFile(u"../asset/images/camera.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.camera_page.setIcon(icon)
        self.camera_page.setIconSize(QSize(32, 32))
        self.tcp_page = QPushButton(self.centralwidget)
        self.tcp_page.setObjectName(u"tcp_page")
        self.tcp_page.setGeometry(QRect(480, 30, 211, 80))
        self.tcp_page.setMinimumSize(QSize(180, 80))
        font = QFont()
        font.setBold(True)
        self.tcp_page.setFont(font)
        icon1 = QIcon()
        icon1.addFile(u"../asset/images/communication.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.tcp_page.setIcon(icon1)
        self.tcp_page.setIconSize(QSize(32, 32))
        self.http_page = QPushButton(self.centralwidget)
        self.http_page.setObjectName(u"http_page")
        self.http_page.setGeometry(QRect(700, 30, 211, 80))
        self.http_page.setMinimumSize(QSize(180, 80))
        icon2 = QIcon()
        icon2.addFile(u"../asset/images/http.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.http_page.setIcon(icon2)
        self.http_page.setIconSize(QSize(48, 32))
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setGeometry(QRect(40, 130, 1841, 911))
        self.stackedWidget.setMinimumSize(QSize(1315, 870))
        self.stackedWidget.setFrameShape(QFrame.NoFrame)
        self.stackedWidget.setLineWidth(1)
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.stackedWidget.addWidget(self.page)
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.stackedWidget.addWidget(self.page_3)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.stackedWidget.addWidget(self.page_2)
        self.model_page = QPushButton(self.centralwidget)
        self.model_page.setObjectName(u"model_page")
        self.model_page.setGeometry(QRect(260, 30, 211, 80))
        self.model_page.setMinimumSize(QSize(180, 80))
        icon3 = QIcon()
        icon3.addFile(u"../asset/images/brain.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.model_page.setIcon(icon3)
        self.model_page.setIconSize(QSize(38, 38))
        self.http_page_2 = QPushButton(self.centralwidget)
        self.http_page_2.setObjectName(u"http_page_2")
        self.http_page_2.setGeometry(QRect(920, 30, 211, 80))
        self.http_page_2.setMinimumSize(QSize(180, 80))
        self.http_page_2.setIcon(icon2)
        self.http_page_2.setIconSize(QSize(48, 32))
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.camera_page.setText(QCoreApplication.translate("MainWindow", u"  CAMERA", None))
        self.tcp_page.setText(QCoreApplication.translate("MainWindow", u"  TCP", None))
        self.http_page.setText(QCoreApplication.translate("MainWindow", u"  HTTP", None))
        self.model_page.setText(QCoreApplication.translate("MainWindow", u"  AI", None))
        self.http_page_2.setText(QCoreApplication.translate("MainWindow", u"  DASH \n"
"  BOARD", None))
    # retranslateUi


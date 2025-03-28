# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dash_board.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QSizePolicy,
    QWidget)

class Ui_dashboard(object):
    def setupUi(self, dashboard):
        if not dashboard.objectName():
            dashboard.setObjectName(u"dashboard")
        dashboard.resize(1650, 830)
        dashboard.setStyleSheet(u"QWidget {\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, \n"
"                                stop:0 #1E1E2E, stop:1 #252836);\n"
"    color: white;\n"
"    font-size: 14px;\n"
"    font-family: \"Segoe UI\", sans-serif;\n"
"}\n"
"")
        self.gridLayoutWidget = QWidget(dashboard)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(0, 0, 1641, 821))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setSpacing(20)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.widget_4 = QWidget(self.gridLayoutWidget)
        self.widget_4.setObjectName(u"widget_4")
        self.widget_4.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"border-radius: 10px;\n"
"\n"
"")
        self.label_4 = QLabel(self.widget_4)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(350, 10, 151, 41))
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setBold(True)
        self.label_4.setFont(font)
        self.label_4.setStyleSheet(u"color: rgb(0, 0, 0);\n"
"font-size: 24px;")
        self.label_4.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.widget_4, 0, 1, 1, 1)

        self.widget = QWidget(self.gridLayoutWidget)
        self.widget.setObjectName(u"widget")
        self.widget.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"border-radius: 10px;\n"
"")
        self.label_2 = QLabel(self.widget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(340, 10, 151, 41))
        self.label_2.setFont(font)
        self.label_2.setStyleSheet(u"color: rgb(0, 0, 0);\n"
"font-size: 24px;")
        self.label_2.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.widget, 1, 0, 1, 1)

        self.widget_3 = QWidget(self.gridLayoutWidget)
        self.widget_3.setObjectName(u"widget_3")
        self.widget_3.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"border-radius: 10px;\n"
"\n"
"")
        self.label = QLabel(self.widget_3)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(330, 10, 151, 41))
        self.label.setFont(font)
        self.label.setStyleSheet(u"color: rgb(0, 0, 0);\n"
"font-size: 24px;")
        self.label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.widget_3, 0, 0, 1, 1)

        self.widget_2 = QWidget(self.gridLayoutWidget)
        self.widget_2.setObjectName(u"widget_2")
        self.widget_2.setStyleSheet(u"background-color: rgb(255, 255, 255);\n"
"border-radius: 10px;\n"
"")
        self.label_3 = QLabel(self.widget_2)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(340, 10, 151, 41))
        self.label_3.setFont(font)
        self.label_3.setStyleSheet(u"color: rgb(0, 0, 0);\n"
"font-size: 24px;")
        self.label_3.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.widget_2, 1, 1, 1, 1)


        self.retranslateUi(dashboard)

        QMetaObject.connectSlotsByName(dashboard)
    # setupUi

    def retranslateUi(self, dashboard):
        dashboard.setWindowTitle(QCoreApplication.translate("dashboard", u"Form", None))
        self.label_4.setText(QCoreApplication.translate("dashboard", u"TOTAL", None))
        self.label_2.setText(QCoreApplication.translate("dashboard", u"TOTAL", None))
        self.label.setText(QCoreApplication.translate("dashboard", u"TOTAL", None))
        self.label_3.setText(QCoreApplication.translate("dashboard", u"TOTAL", None))
    # retranslateUi


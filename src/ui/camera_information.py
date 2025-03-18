# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'camera_information.ui'
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
    QLineEdit, QPushButton, QSizePolicy, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(306, 356)
        self.layoutWidget = QWidget(Form)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(20, 30, 271, 241))
        self.gridLayout_2 = QGridLayout(self.layoutWidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.cam_ip = QLineEdit(self.layoutWidget)
        self.cam_ip.setObjectName(u"cam_ip")
        font = QFont()
        font.setPointSize(12)
        self.cam_ip.setFont(font)

        self.gridLayout_2.addWidget(self.cam_ip, 1, 1, 1, 1)

        self.label_7 = QLabel(self.layoutWidget)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setMinimumSize(QSize(100, 0))
        self.label_7.setFont(font)

        self.gridLayout_2.addWidget(self.label_7, 3, 0, 1, 1)

        self.cam_port = QLineEdit(self.layoutWidget)
        self.cam_port.setObjectName(u"cam_port")
        self.cam_port.setFont(font)

        self.gridLayout_2.addWidget(self.cam_port, 2, 1, 1, 1)

        self.cam_user = QLineEdit(self.layoutWidget)
        self.cam_user.setObjectName(u"cam_user")
        self.cam_user.setFont(font)

        self.gridLayout_2.addWidget(self.cam_user, 3, 1, 1, 1)

        self.label = QLabel(self.layoutWidget)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(100, 0))
        self.label.setFont(font)

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.label_13 = QLabel(self.layoutWidget)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setMinimumSize(QSize(100, 0))
        self.label_13.setFont(font)

        self.gridLayout_2.addWidget(self.label_13, 4, 0, 1, 1)

        self.label_2 = QLabel(self.layoutWidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(100, 0))
        self.label_2.setFont(font)

        self.gridLayout_2.addWidget(self.label_2, 2, 0, 1, 1)

        self.cam_name = QLineEdit(self.layoutWidget)
        self.cam_name.setObjectName(u"cam_name")
        self.cam_name.setFont(font)

        self.gridLayout_2.addWidget(self.cam_name, 0, 1, 1, 1)

        self.cam_pass = QLineEdit(self.layoutWidget)
        self.cam_pass.setObjectName(u"cam_pass")
        self.cam_pass.setFont(font)

        self.gridLayout_2.addWidget(self.cam_pass, 4, 1, 1, 1)

        self.label_14 = QLabel(self.layoutWidget)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setMinimumSize(QSize(100, 0))
        self.label_14.setFont(font)

        self.gridLayout_2.addWidget(self.label_14, 6, 0, 1, 1)

        self.label_3 = QLabel(self.layoutWidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(100, 0))
        self.label_3.setFont(font)

        self.gridLayout_2.addWidget(self.label_3, 1, 0, 1, 1)

        self.comboBox = QComboBox(self.layoutWidget)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setFont(font)

        self.gridLayout_2.addWidget(self.comboBox, 6, 1, 1, 1)

        self.ok_button = QPushButton(Form)
        self.ok_button.setObjectName(u"ok_button")
        self.ok_button.setGeometry(QRect(64, 300, 81, 31))
        self.ok_button.setFont(font)
        self.cancel_button = QPushButton(Form)
        self.cancel_button.setObjectName(u"cancel_button")
        self.cancel_button.setGeometry(QRect(164, 300, 81, 31))
        self.cancel_button.setFont(font)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Add Camera", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"User name:", None))
        self.label.setText(QCoreApplication.translate("Form", u"Camera Name:", None))
        self.label_13.setText(QCoreApplication.translate("Form", u"Password:", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Port:", None))
        self.label_14.setText(QCoreApplication.translate("Form", u"Protocols", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"IP Adress:", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("Form", u"RTSP", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("Form", u"HTTP", None))

        self.ok_button.setText(QCoreApplication.translate("Form", u"OK", None))
        self.cancel_button.setText(QCoreApplication.translate("Form", u"Cancel", None))
    # retranslateUi


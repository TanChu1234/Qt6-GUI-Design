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
        Form.resize(1315, 830)
        self.layoutWidget = QWidget(Form)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(9, 20, 1301, 801))
        self.gridLayout = QGridLayout(self.layoutWidget)
        self.gridLayout.setSpacing(8)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setHorizontalSpacing(8)
        self.gridLayout_2.setVerticalSpacing(0)
        self.add_cam = QPushButton(self.layoutWidget)
        self.add_cam.setObjectName(u"add_cam")
        self.add_cam.setMinimumSize(QSize(100, 60))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.add_cam.setFont(font)

        self.gridLayout_2.addWidget(self.add_cam, 0, 0, 1, 1)

        self.remove_cam = QPushButton(self.layoutWidget)
        self.remove_cam.setObjectName(u"remove_cam")
        self.remove_cam.setMinimumSize(QSize(100, 60))
        self.remove_cam.setFont(font)

        self.gridLayout_2.addWidget(self.remove_cam, 0, 1, 1, 1)


        self.gridLayout.addLayout(self.gridLayout_2, 9, 0, 1, 1)

        self.label = QLabel(self.layoutWidget)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(1080, 720))
        self.label.setSizeIncrement(QSize(0, 0))
        self.label.setStyleSheet(u"background-color: rgb(0, 0, 127);")
        self.label.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.label, 4, 1, 5, 12)

        self.listWidget = QListWidget(self.layoutWidget)
        QListWidgetItem(self.listWidget)
        self.listWidget.setObjectName(u"listWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget.sizePolicy().hasHeightForWidth())
        self.listWidget.setSizePolicy(sizePolicy)
        self.listWidget.setMinimumSize(QSize(200, 0))
        self.listWidget.setSizeIncrement(QSize(0, 0))
        font1 = QFont()
        font1.setPointSize(12)
        self.listWidget.setFont(font1)
        self.listWidget.setFlow(QListView.TopToBottom)

        self.gridLayout.addWidget(self.listWidget, 4, 0, 5, 1)

        self.start_cam = QPushButton(self.layoutWidget)
        self.start_cam.setObjectName(u"start_cam")
        self.start_cam.setMinimumSize(QSize(100, 60))
        self.start_cam.setFont(font)

        self.gridLayout.addWidget(self.start_cam, 9, 1, 1, 1)

        self.stop_cam = QPushButton(self.layoutWidget)
        self.stop_cam.setObjectName(u"stop_cam")
        self.stop_cam.setMinimumSize(QSize(100, 60))
        self.stop_cam.setFont(font)

        self.gridLayout.addWidget(self.stop_cam, 9, 2, 1, 1)

        self.display = QPushButton(self.layoutWidget)
        self.display.setObjectName(u"display")
        self.display.setMinimumSize(QSize(100, 60))
        self.display.setFont(font)

        self.gridLayout.addWidget(self.display, 9, 3, 1, 1)

        self.run_once = QPushButton(self.layoutWidget)
        self.run_once.setObjectName(u"run_once")
        self.run_once.setMinimumSize(QSize(100, 60))
        self.run_once.setFont(font)

        self.gridLayout.addWidget(self.run_once, 9, 4, 1, 1)

        self.run_continuous = QPushButton(self.layoutWidget)
        self.run_continuous.setObjectName(u"run_continuous")
        self.run_continuous.setMinimumSize(QSize(100, 60))
        self.run_continuous.setFont(font)

        self.gridLayout.addWidget(self.run_continuous, 9, 5, 1, 1)

        self.label_2 = QLabel(self.layoutWidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(70, 60))
        self.label_2.setFont(font)
        self.label_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.label_2.setIndent(5)

        self.gridLayout.addWidget(self.label_2, 9, 6, 1, 1)

        self.log_list = QListWidget(self.layoutWidget)
        self.log_list.setObjectName(u"log_list")
        self.log_list.setMinimumSize(QSize(0, 60))

        self.gridLayout.addWidget(self.log_list, 9, 7, 1, 6)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.add_cam.setText(QCoreApplication.translate("Form", u"ADD CAM", None))
        self.remove_cam.setText(QCoreApplication.translate("Form", u"DEL CAM", None))
        self.label.setText("")

        __sortingEnabled = self.listWidget.isSortingEnabled()
        self.listWidget.setSortingEnabled(False)
        ___qlistwidgetitem = self.listWidget.item(0)
        ___qlistwidgetitem.setText(QCoreApplication.translate("Form", u"Camera ", None));
        self.listWidget.setSortingEnabled(__sortingEnabled)

        self.start_cam.setText(QCoreApplication.translate("Form", u"START", None))
        self.stop_cam.setText(QCoreApplication.translate("Form", u"STOP", None))
        self.display.setText(QCoreApplication.translate("Form", u"DISPLAY", None))
        self.run_once.setText(QCoreApplication.translate("Form", u"RUN AI \n"
"ONCE TIME", None))
        self.run_continuous.setText(QCoreApplication.translate("Form", u"RUN AI \n"
"REAL TIME", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"LOG:", None))
    # retranslateUi


# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'downloader.ui'
##
## Created by: Qt User Interface Compiler version 6.5.3
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLineEdit, QListWidget,
    QListWidgetItem, QPushButton, QSizePolicy, QSpacerItem,
    QToolButton, QVBoxLayout, QWidget)
import res.resource_rc

class Ui_Downloader(object):
    def setupUi(self, Downloader):
        if not Downloader.objectName():
            Downloader.setObjectName(u"Downloader")
        Downloader.resize(360, 653)
        Downloader.setStyleSheet(u"")
        self.verticalLayout = QVBoxLayout(Downloader)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.urlEdit = QLineEdit(Downloader)
        self.urlEdit.setObjectName(u"urlEdit")
        self.urlEdit.setMinimumSize(QSize(32, 32))

        self.horizontalLayout.addWidget(self.urlEdit)

        self.pasteButton = QToolButton(Downloader)
        self.pasteButton.setObjectName(u"pasteButton")
        icon = QIcon()
        icon.addFile(u":/icon/icon/\u7c98\u8d34.png", QSize(), QIcon.Normal, QIcon.On)
        self.pasteButton.setIcon(icon)
        self.pasteButton.setIconSize(QSize(32, 32))

        self.horizontalLayout.addWidget(self.pasteButton)

        self.downloadButton = QToolButton(Downloader)
        self.downloadButton.setObjectName(u"downloadButton")
        icon1 = QIcon()
        icon1.addFile(u":/icon/icon/\u4e0b\u8f7d.png", QSize(), QIcon.Normal, QIcon.On)
        self.downloadButton.setIcon(icon1)
        self.downloadButton.setIconSize(QSize(32, 32))

        self.horizontalLayout.addWidget(self.downloadButton)


        self.horizontalLayout_3.addLayout(self.horizontalLayout)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.infoWidget = QListWidget(Downloader)
        self.infoWidget.setObjectName(u"infoWidget")
        self.infoWidget.setStyleSheet(u"QListView \n"
"{\n"
"      show-decoration-selected: 1;\n"
"}\n"
" \n"
"QListView::item:alternate \n"
"{\n"
"      background: #EEEEEE;\n"
"}\n"
" \n"
"QListView::item:selected \n"
"{\n"
"      border: 1px solid #d4d4d4;\n"
"}\n"
" \n"
"QListView::item:selected:!active \n"
"{\n"
"	background-color: qlineargradient(spread:pad, x1:1, y1:0.0284091, x2:0, y2:0, stop:0.278607 rgba(252, 210, 171, 255), stop:1 rgba(255, 255, 255, 255));\n"
"}\n"
" \n"
"QListView::item:selected:active\n"
"{\n"
"	background-color: qlineargradient(spread:pad, x1:1, y1:0.0284091, x2:0, y2:0, stop:0.278607 rgba(245, 252, 171, 255), stop:1 rgba(255, 255, 255, 255));\n"
"}\n"
" \n"
"QListView::item:hover\n"
"{\n"
"      background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
"                                  stop: 0 #FAFBFE, stop: 1 #DCDEF1);\n"
"}\n"
"\n"
"//\u9002\u7528\u4e8e\u5f00\u542f\u4ea4\u66ff\u989c\u8272\n"
"QListWidget#listWidget\n"
"{\n"
"    alternate-background-color:blue;\n"
"	background:yellow\n"
"}")

        self.horizontalLayout_2.addWidget(self.infoWidget)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.exitButton = QToolButton(Downloader)
        self.exitButton.setObjectName(u"exitButton")
        icon2 = QIcon()
        icon2.addFile(u":/icon/icon/\u5173\u95ed.png", QSize(), QIcon.Normal, QIcon.On)
        self.exitButton.setIcon(icon2)
        self.exitButton.setIconSize(QSize(32, 32))

        self.horizontalLayout_4.addWidget(self.exitButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.mergeButton = QPushButton(Downloader)
        self.mergeButton.setObjectName(u"mergeButton")
        self.mergeButton.setMinimumSize(QSize(32, 32))
        self.mergeButton.setIconSize(QSize(32, 32))

        self.horizontalLayout_4.addWidget(self.mergeButton)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 10)

        self.retranslateUi(Downloader)
        self.exitButton.clicked.connect(Downloader.close)

        self.infoWidget.setCurrentRow(-1)


        QMetaObject.connectSlotsByName(Downloader)
    # setupUi

    def retranslateUi(self, Downloader):
        Downloader.setWindowTitle(QCoreApplication.translate("Downloader", u"Form", None))
        self.pasteButton.setText("")
        self.downloadButton.setText("")
        self.exitButton.setText("")
        self.mergeButton.setText(QCoreApplication.translate("Downloader", u"merge", None))
    # retranslateUi


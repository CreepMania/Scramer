# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtWidgets
from sys import argv
import Scraper


class ScraperWindow(object):

    # MainWindow = QtWidgets.QMainWindow()

    def __init__(self, main_window, app):
        self.app = app
        self.MainWindow = main_window
        self.MainWindow.setObjectName("Scraper")
        self.MainWindow.resize(700, 500)
        self.MainWindow.setMinimumSize(QtCore.QSize(700, 500))
        self.centralWidget = QtWidgets.QWidget(self.MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralWidget)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.centralWidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.filePath = QtWidgets.QLineEdit(self.centralWidget)
        self.filePath.setObjectName("filePath")
        self.filePath.setText('/home/guillaume/PycharmProjects/Scrapper1.0/test.csv')
        self.horizontalLayout.addWidget(self.filePath)

        self.pushButton = QtWidgets.QPushButton(self.centralWidget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.progressBar = QtWidgets.QProgressBar(self.centralWidget)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")

        self.verticalLayout.addWidget(self.progressBar)
        self.textBrowser = QtWidgets.QTextBrowser(self.centralWidget)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)
        self.MainWindow.setCentralWidget(self.centralWidget)
        self.statusBar = QtWidgets.QStatusBar(self.MainWindow)
        self.statusBar.setObjectName("statusBar")
        self.MainWindow.setStatusBar(self.statusBar)

        self.menuBar = QtWidgets.QMenuBar(self.MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 700, 23))
        self.menuBar.setObjectName("menuBar")

        self.menuFile = QtWidgets.QMenu(self.menuBar)
        self.menuFile.setObjectName("menuFile")
        self.MainWindow.setMenuBar(self.menuBar)

        self.actionOpen_File = QtWidgets.QAction("&Open File")
        self.actionOpen_File.setObjectName("actionOpen_File")
        self.actionOpen_File.setShortcut("Ctrl+O")
        self.actionOpen_File.setStatusTip("Open a file")
        self.actionOpen_File.triggered.connect(self.open_file)

        self.pushButton.clicked.connect(self._call_scraping)

        self.menuFile.addAction(self.actionOpen_File)
        self.menuBar.addAction(self.menuFile.menuAction())

        self._retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self.MainWindow)

    def _retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.MainWindow.setWindowTitle(_translate("MainWindow", "Scraper"))
        self.label.setText(_translate("MainWindow", "File Name:"))
        self.pushButton.setText(_translate("MainWindow", "Start"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionOpen_File.setText(_translate("MainWindow", "Open File"))

    def open_file(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Open CSV File", "",
                                                             "CSV Files (*.csv)", options=options)
        if file_name:
            self.filePath.setText(file_name)

    def add_text(self, text):
        self.textBrowser.append(text)

    def _call_scraping(self):
        self.textBrowser.clear()
        self.progressBar.setValue(0)
        self.app.scrape()

    def emptyPathErr(self):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setWindowTitle('Error')
        msg.setText('Empty File Path !')
        msg.exec_()

    def fileNotFoundErr(self):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setWindowTitle('Error')
        msg.setText('File Not Found !')
        msg.exec_()

    def jobDone(self):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle('Done')
        msg.setText('Job Done !')
        msg.exec_()
        self.add_text('Done.')

    def isADirectoryErr(self):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setWindowTitle('Error')
        msg.setText('The path entered does not lead to a file !')
        msg.exec_()

    def setMaxProgressBar(self, value):
        self.progressBar.setMaximum(value)

    def iterateProgressBar(self):
        self.progressBar.setValue(self.progressBar.value() + 1)

    def get_filepath(self):
        return self.filePath.text()

    def show(self):
        self.MainWindow.show()

    def isVisible(self):
        return self.MainWindow.isVisible()

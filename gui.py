# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_pdf_ocr(object):
    def setupUi(self, pdf_ocr):
        pdf_ocr.setObjectName("pdf_ocr")
        pdf_ocr.resize(775, 445)
        self.centralwidget = QtWidgets.QWidget(pdf_ocr)
        self.centralwidget.setObjectName("centralwidget")
        self.ocrMethod = QtWidgets.QComboBox(self.centralwidget)
        self.ocrMethod.setGeometry(QtCore.QRect(310, 330, 100, 30))
        self.ocrMethod.setObjectName("ocrMethod")
        self.ocrMethod.addItem("")
        self.ocrMethod.addItem("")
        self.ocrMethod.addItem("")
        self.start = QtWidgets.QPushButton(self.centralwidget)
        self.start.setGeometry(QtCore.QRect(430, 330, 100, 32))
        self.start.setObjectName("start")
        self.langBox = QtWidgets.QComboBox(self.centralwidget)
        self.langBox.setGeometry(QtCore.QRect(220, 330, 75, 30))
        self.langBox.setObjectName("langBox")
        self.langBox.addItem("")
        self.langBox.addItem("")
        self.langBox.addItem("")
        self.pdfTable = QtWidgets.QTableWidget(self.centralwidget)
        self.pdfTable.setGeometry(QtCore.QRect(60, 70, 641, 192))
        self.pdfTable.setObjectName("pdfTable")
        self.pdfTable.setColumnCount(0)
        self.pdfTable.setRowCount(0)
        self.outdirLabel = QtWidgets.QLabel(self.centralwidget)
        self.outdirLabel.setGeometry(QtCore.QRect(60, 284, 72, 20))
        self.outdirLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.outdirLabel.setObjectName("outdirLabel")
        self.outdir = QtWidgets.QLineEdit(self.centralwidget)
        self.outdir.setGeometry(QtCore.QRect(140, 285, 451, 20))
        self.outdir.setObjectName("outdir")
        self.outdirButton = QtWidgets.QPushButton(self.centralwidget)
        self.outdirButton.setGeometry(QtCore.QRect(610, 282, 92, 25))
        self.outdirButton.setObjectName("outdirButton")
        self.pdfLabel = QtWidgets.QLabel(self.centralwidget)
        self.pdfLabel.setGeometry(QtCore.QRect(60, 50, 72, 15))
        self.pdfLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.pdfLabel.setObjectName("pdfLabel")
        pdf_ocr.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(pdf_ocr)
        self.statusbar.setObjectName("statusbar")
        pdf_ocr.setStatusBar(self.statusbar)

        self.retranslateUi(pdf_ocr)
        QtCore.QMetaObject.connectSlotsByName(pdf_ocr)

    def retranslateUi(self, pdf_ocr):
        _translate = QtCore.QCoreApplication.translate
        pdf_ocr.setWindowTitle(_translate("pdf_ocr", "pdf_ocr"))
        self.ocrMethod.setItemText(0, _translate("pdf_ocr", "paddle"))
        self.ocrMethod.setItemText(1, _translate("pdf_ocr", "easy"))
        self.ocrMethod.setItemText(2, _translate("pdf_ocr", "online"))
        self.start.setText(_translate("pdf_ocr", "开始识别"))
        self.langBox.setItemText(0, _translate("pdf_ocr", "ch_sim"))
        self.langBox.setItemText(1, _translate("pdf_ocr", "en"))
        self.langBox.setItemText(2, _translate("pdf_ocr", "dual"))
        self.outdirLabel.setText(_translate("pdf_ocr", "输出目录"))
        self.outdirButton.setText(_translate("pdf_ocr", "浏览"))
        self.pdfLabel.setText(_translate("pdf_ocr", "工作区"))
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QPushButton, QHBoxLayout

import pdfmerge
import os


class UiPDFMerger(object):
    def setupUi(self, PDFMerger):
        PDFMerger.setObjectName("PDFMerger")
        PDFMerger.resize(471, 427)
        self.centralwidget = QtWidgets.QWidget(PDFMerger)
        self.centralwidget.setObjectName("centralwidget")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)

        # List of files to be merged
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setGeometry(QtCore.QRect(20, 30, 331, 192))
        self.listWidget.setObjectName("listWidget")

        # Add Files
        self.btnAdd = QtWidgets.QPushButton(self.centralwidget)
        self.btnAdd.setGeometry(QtCore.QRect(360, 60, 93, 28))
        self.btnAdd.setObjectName("btnAdd")

        # Move Down
        self.btnMoveDown = QtWidgets.QPushButton(self.centralwidget)
        self.btnMoveDown.setGeometry(QtCore.QRect(360, 90, 93, 28))
        self.btnMoveDown.setObjectName("btnMoveDown")

        # Move Up
        self.btnMoveUp = QtWidgets.QPushButton(self.centralwidget)
        self.btnMoveUp.setGeometry(QtCore.QRect(360, 120, 93, 28))
        self.btnMoveUp.setObjectName("btnMoveUp")

        # Delete
        self.btnDelete = QtWidgets.QPushButton(self.centralwidget)
        self.btnDelete.setGeometry(QtCore.QRect(360, 150, 93, 28))
        self.btnDelete.setObjectName("btnDelete")

        # Merge
        self.btnMerge = QtWidgets.QPushButton(self.centralwidget)
        self.btnMerge.setGeometry(QtCore.QRect(120, 330, 151, 41))
        self.btnMerge.setObjectName("btnMerge")

        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(20, 240, 331, 31))
        self.lineEdit.setObjectName("lineEdit")

        # Output Directory
        self.btnOutDir = QtWidgets.QPushButton(self.centralwidget)
        self.btnOutDir.setGeometry(QtCore.QRect(360, 240, 93, 28))
        self.btnOutDir.setObjectName("btnOutDir")

        # Output Filename
        self.outputFile = QtWidgets.QLineEdit(self.centralwidget)
        self.outputFile.setGeometry(QtCore.QRect(20, 280, 331, 31))
        self.outputFile.setObjectName("outputFile")

        PDFMerger.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(PDFMerger)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 458, 25))
        self.menubar.setObjectName("menubar")
        PDFMerger.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(PDFMerger)
        self.statusbar.setObjectName("statusbar")
        PDFMerger.setStatusBar(self.statusbar)

        _translate = QtCore.QCoreApplication.translate

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(170, 390, 131, 20))
        self.label.setObjectName("label")

        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(20, 10, 301, 20))
        self.label_2.setObjectName("label_2")

        self.retranslateUi(PDFMerger, _translate)
        QtCore.QMetaObject.connectSlotsByName(PDFMerger)
        
        self.btnAdd.clicked.connect(lambda: self.addButtonClicked())
        self.btnMoveUp.clicked.connect(lambda: self.moveUpButtonClicked())
        self.btnMoveDown.clicked.connect(lambda: self.moveDownButtonClicked())
        self.btnDelete.clicked.connect(lambda: self.deleteButtonClicked())
        self.btnOutDir.clicked.connect(lambda: self.outDirButtonClicked())
        self.btnMerge.clicked.connect(lambda: self.mergeButtonClicked())

    def retranslateUi(self, PDFMerger, _translate):
        PDFMerger.setWindowTitle(_translate("PDFMerger", "PDF Merge"))
        PDFMerger.setWindowIcon(QIcon('images/pdf2.png'))
        self.btnAdd.setText(_translate("PDF Merger", "Add Files"))
        self.btnMoveUp.setText(_translate("PDF Merger", "Move Up"))
        self.btnMoveDown.setText(_translate("PDF Merger", "Move Down"))
        self.btnDelete.setText(_translate("PDF Merger", "Delete"))
        self.btnMerge.setText(_translate("PDFMerger", "Merge PDFs"))
        self.lineEdit.setPlaceholderText(_translate("PDF Merger", "Output Directory"))
        self.btnOutDir.setText(_translate("PDF Merger", "Output"))
        self.outputFile.setPlaceholderText(_translate("PDFMerger", "Output Filename"))
        self.label_2.setText(_translate("PDFMerger", "Files will be merged in the below order"))

    def addButtonClicked(self):
        filter_mask = "Supported files (*.pdf *.png *.jpg *.jpeg *.bmp *.tif *.tiff *.gif *.txt)"
        caption = "Open Files"
        selected = QFileDialog.getOpenFileNames(None, caption, '', filter_mask)
        paths = selected[0]
        for p in paths:
            if p:
                self.listWidget.addItem(p)

    def moveUpButtonClicked(self):
        self.currentRow = self.listWidget.currentRow()
        if self.currentRow == -1:
            self.showdialog("Select an item to move")
            return
        else:
            if self.currentRow == 0:
                return
            else:
                self.currentItem = self.listWidget.takeItem(self.currentRow)
                self.listWidget.insertItem(self.currentRow - 1, self.currentItem)
                self.currentRow = self.currentRow - 1
                self.listWidget.setCurrentRow(self.currentRow)

    def moveDownButtonClicked(self):
        self.currentRow = self.listWidget.currentRow()

        if self.currentRow == -1:
            self.showdialog("Select an item to move")
            return
        else:
            if self.currentRow >= self.listWidget.count() - 1:
                return
            self.currentItem = self.listWidget.takeItem(self.currentRow)
            self.listWidget.insertItem(self.currentRow + 1, self.currentItem)
            self.currentRow = self.currentRow + 1
            self.listWidget.setCurrentRow(self.currentRow)

    def deleteButtonClicked(self):
        self.currentRow = self.listWidget.currentRow()
        if self.currentRow != -1:
            self.listWidget.takeItem(self.currentRow)

    def outDirButtonClicked(self):
        self.outputfolder = QFileDialog.getExistingDirectory()
        _translate = QtCore.QCoreApplication.translate
        self.lineEdit.setText(_translate("PDFMerger", self.outputfolder))

    def mergeButtonClicked(self):
        _translate = QtCore.QCoreApplication.translate
        # Validate inputs
        if self.lineEdit.text().strip() == "":
            self.showdialog("Select Output Directory")
            return
        if self.outputFile.text().strip() == "":
            self.showdialog("Enter an output filename")
            return
        if self.listWidget.count() == 0:
            self.showdialog("Add PDFs to merge")
            return

        try:
            readFileList = [self.listWidget.item(i).text() for i in range(self.listWidget.count())]
            # Determine output path
            out_dir = self.lineEdit.text().strip()
            out_name = self.outputFile.text().strip()
            out_path = os.path.join(out_dir, f"{out_name}.pdf")

            # Ask for overwrite if file exists
            if os.path.exists(out_path):
                reply = QMessageBox.question(
                    None,
                    "Overwrite file?",
                    f"Output file already exists:\n{out_path}\n\nDo you want to overwrite it?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if reply != QMessageBox.Yes:
                    return

            self.label.setText(_translate("PDF Merger", "Merging... Please wait..."))
            self.label.setStyleSheet("color:white")
            self.label.repaint()

            # Use updated merge utility with overwrite=True (user confirmed if necessary)
            pdfmerge.merge_pdfs(readFileList, out_path, overwrite=True)

            self.label.setText(_translate("PDF Merger", "Merged Successfully!"))
            self.label.setStyleSheet("color:green")
            self.label.repaint()
        except Exception as e:
            # Display error
            self.showdialog(f"Merge failed: {e}")

    def showdialog(self, displaytext):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Warning")
        msg.setWindowIcon(QIcon('images/warning.png'))
        msg.setText(displaytext)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    style = """
        QWidget{
            background : #191970;
            font-size: 13px;
            color : #fff
        
        }
        QLabel{
            color : #fff;
            font-size: 13px;
            font-weight: bold;
        }
        QPushButton {
            color: #fff;
            background-color: #4169E1;
            border-width: 1px;
            border-color: #1e1e1e;
            border-style: solid;
            border-radius: 8px;
            padding: 3px;
            font-size: 14px;
            padding-left: 5px;
            padding-right: 5px;
            min-width: 60px;
        }
        QPushButton:hover{
            border: 1px #C6C6C6 solid;
            color: #fff;
            background: #0892D0;
        }
        QLineEdit {
            padding: 1px;
            color: #fff;
            border-style: solid;
            border: 2px solid #fff;
            border-radius: 8px;
        }

    """
    app.setStyleSheet(style)
    PDFMerger = QtWidgets.QMainWindow()
    ui = UiPDFMerger()
    ui.setupUi(PDFMerger)
    PDFMerger.show()
    sys.exit(app.exec_())

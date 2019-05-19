# -*- coding: utf-8 -*-
"""novelWriter GUI Project Editor

 novelWriter – GUI Project Editor
===================================
 Class holding the project editor

 File History:
 Created: 2018-09-29 [0.0.1]

"""

import logging
import nw

from os              import path

from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QGroupBox, QFormLayout, QLineEdit, QPlainTextEdit,
    QPushButton, QWidget, QTabWidget
)
from PyQt5.QtSvg     import QSvgWidget

logger = logging.getLogger(__name__)

class GuiProjectEditor(QDialog):

    def __init__(self, theParent, theProject):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising ProjectEditor ...")

        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.outerBox   = QHBoxLayout()
        self.innerBox   = QVBoxLayout()

        self.setWindowTitle("Project Settings")

        self.gradPath = path.abspath(path.join(self.mainConf.appPath,"graphics","block.svg"))
        self.svgGradient = QSvgWidget(self.gradPath)
        self.svgGradient.setFixedWidth(80)

        # self.tabWidget = QTabWidget()

        self.setLayout(self.outerBox)
        self.outerBox.addWidget(self.svgGradient)
        self.outerBox.addLayout(self.innerBox)

        self.tabSettings = GuiProjectEditMain(self.theProject)

        self.buttonBox = QHBoxLayout()
        self.closeButton = QPushButton("Close")
        self.closeButton.clicked.connect(self._doClose)
        self.saveButton = QPushButton("Save")
        self.saveButton.clicked.connect(self._doSave)
        self.buttonBox.addStretch(1)
        self.buttonBox.addWidget(self.closeButton)
        self.buttonBox.addWidget(self.saveButton)

        # self.mainGroup.setLayout(self.mainForm)
        self.innerBox.addWidget(self.tabSettings)
        self.innerBox.addLayout(self.buttonBox)

        self.show()

        logger.debug("ProjectEditor initialisation complete")

        return

    def _doSave(self):
        logger.verbose("ProjectEditor save button clicked")
        projName    = self.editName.text()
        bookTitle   = self.editTitle.text()
        bookAuthors = self.editAuthors.toPlainText()
        self.theProject.setProjectName(projName)
        self.theProject.setBookTitle(bookTitle)
        self.theProject.setBookAuthors(bookAuthors)
        self.theProject.setProjectChanged(True)
        self.close()
        return

    def _doClose(self):
        logger.verbose("ProjectEditor close button clicked")
        self.close()
        return

# END Class GuiProjectEditor

class GuiProjectEditMain(QGroupBox):

    def __init__(self, theProject):
        QGroupBox.__init__(self)

        self.theProject = theProject

        # self.mainGroup = QGroupBox("Project Settings")
        self.setTitle("Project Settings")
        self.mainForm  = QFormLayout()

        self.editName    = QLineEdit()
        self.editTitle   = QLineEdit()
        self.editAuthors = QPlainTextEdit()

        self.mainForm.addRow("Working Title", self.editName)
        self.mainForm.addRow("Book Title",    self.editTitle)
        self.mainForm.addRow("Book Authors",  self.editAuthors)

        self.editName.setText(self.theProject.projName)
        self.editTitle.setText(self.theProject.bookTitle)
        bookAuthors = ""
        for bookAuthor in self.theProject.bookAuthors:
            bookAuthors += bookAuthor+"\n"
        self.editAuthors.setPlainText(bookAuthors)

        self.setLayout(self.mainForm)

        return

# END Class GuiProjectEditMain

# -*- coding: utf-8 -*-
"""novelWriter GUI Item Editor

 novelWriter – GUI Item Editor
===============================
 Class holding the item editor

 File History:
 Created: 2019-04-27 [0.0.1]

"""

import logging
import nw

from os              import path

from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QGroupBox, QFormLayout, QLineEdit, QPushButton
from PyQt5.QtSvg     import QSvgWidget

logger = logging.getLogger(__name__)

class GuiItemEditor(QDialog):

    def __init__(self, guiParent, theProject, tHandle):
        QDialog.__init__(self, guiParent)

        logger.debug("Initialising ItemEditor ...")

        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.theItem    = self.theProject.getItem(tHandle)

        self.outerBox   = QHBoxLayout()
        self.innerBox   = QVBoxLayout()

        self.setWindowTitle("Item Settings")

        self.gradPath = path.abspath(path.join(self.mainConf.appPath,"graphics","block.svg"))
        self.svgGradient = QSvgWidget(self.gradPath)
        self.svgGradient.setFixedWidth(80)
        self.setLayout(self.outerBox)
        self.outerBox.addWidget(self.svgGradient)
        self.outerBox.addLayout(self.innerBox)

        self.mainGroup = QGroupBox("Item Settings")
        self.mainForm  = QFormLayout()

        self.editName   = QLineEdit()
        self.editStatus = QLineEdit()
        self.editLayout = QLineEdit()

        self.mainForm.addRow("Name",   self.editName)
        self.mainForm.addRow("Status", self.editStatus)
        self.mainForm.addRow("Layout", self.editLayout)

        self.editName.setText(self.theItem.itemName)
        self.editStatus.setText(str(self.theItem.itemStatus))
        self.editLayout.setText(str(self.theItem.itemLayout))

        self.buttonBox = QHBoxLayout()
        self.closeButton = QPushButton("Close")
        self.closeButton.clicked.connect(self._doClose)
        self.saveButton = QPushButton("Save")
        self.saveButton.clicked.connect(self._doSave)
        self.buttonBox.addStretch(1)
        self.buttonBox.addWidget(self.closeButton)
        self.buttonBox.addWidget(self.saveButton)

        self.mainGroup.setLayout(self.mainForm)
        self.innerBox.addWidget(self.mainGroup)
        self.innerBox.addLayout(self.buttonBox)

        self.show()

        logger.debug("ItemEditor initialisation complete")

        return

    def _doSave(self):
        logger.verbose("ItemEditor save button clicked")
        # projName    = self.editName.text()
        # bookTitle   = self.editTitle.text()
        # bookAuthors = self.editAuthors.toPlainText()
        # self.theProject.setProjectName(projName)
        # self.theProject.setBookTitle(bookTitle)
        # self.theProject.setBookAuthors(bookAuthors)
        return

    def _doClose(self):
        logger.verbose("ItemEditor close button clicked")
        self.close()
        return

# END Class GuiItemEditor

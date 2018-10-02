# -*- coding: utf-8 -*
"""novelWriter GUI Project Editor

 novelWriter – GUI Project Editor
===================================
 Class holding the project editor

 File History:
 Created: 2018-09-29 [0.1.0]

"""

import logging
import nw

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, QFormLayout, QLabel, QLineEdit, QPlainTextEdit, QPushButton, QFileDialog
from PyQt5.QtGui     import QIcon

logger = logging.getLogger(__name__)

class GuiProjectEditor(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        logger.debug("Initialising ProjectEditor ...")

        self.outerBox = QVBoxLayout()
        self.setLayout(self.outerBox)

        self.mainGroup = QGroupBox("Project Settings")
        self.mainForm  = QFormLayout()

        self.editName    = QLineEdit()
        self.editTitle   = QLineEdit()
        self.editAuthors = QPlainTextEdit()
        self.saveBox     = QHBoxLayout()
        self.savePath    = QLineEdit()
        self.saveButton  = QPushButton(QIcon.fromTheme("folder"),"Browse")
        self.saveButton.setToolTip("Browse for Save Path")
        self.saveButton.clicked.connect(self._browseProjectPath)
        self.saveBox.addWidget(self.savePath)
        self.saveBox.addWidget(self.saveButton)

        self.mainForm.addRow("Working Name", self.editName)
        self.mainForm.addRow("Book Title",   self.editTitle)
        self.mainForm.addRow("Book Authors", self.editAuthors)
        self.mainForm.addRow("Save Path",    self.saveBox)

        self.mainGroup.setLayout(self.mainForm)
        self.outerBox.addWidget(self.mainGroup)

        logger.debug("ProjectEditor initialisation complete")

        return

    def _browseProjectPath(self):
        fileName, _ = QFileDialog.getSaveFileName(self,"Project File Name","","novelWriter File (*.nwf);;All Files (*)")
        self.savePath.setText(fileName)
        return

# END Class GuiProjectEditor

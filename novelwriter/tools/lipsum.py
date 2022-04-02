"""
novelWriter – Lorem Ipsum Tool
==============================
Simple tool for inserting placeholder text in a document

File History:
Created: 2022-04-02 [1.7a0]

This file is a part of novelWriter
Copyright 2018–2022, Veronica Berglyd Olsen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import os
import random
import logging
import novelwriter

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QDialogButtonBox,
    QSpinBox
)

from novelwriter.gui.custom import QSwitch
from novelwriter.common import readTextFile

logger = logging.getLogger(__name__)


class GuiLipsum(QDialog):

    def __init__(self, theParent):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiLipsum ...")
        self.setObjectName("GuiLipsum")

        self.mainConf  = novelwriter.CONFIG
        self.theParent = theParent
        self.theTheme  = theParent.theTheme

        self.setWindowTitle(self.tr("Insert Placeholder Text"))

        self.innerBox = QHBoxLayout()
        self.innerBox.setSpacing(self.mainConf.pxInt(16))

        # Icon
        nPx = self.mainConf.pxInt(64)
        vSp = self.mainConf.pxInt(4)
        self.docIcon = QLabel()
        self.docIcon.setPixmap(self.theParent.theTheme.getPixmap("proj_document", (nPx, nPx)))

        self.leftBox = QVBoxLayout()
        self.leftBox.setSpacing(vSp)
        self.leftBox.addWidget(self.docIcon)
        self.leftBox.addStretch(1)
        self.innerBox.addLayout(self.leftBox)

        # Form
        self.headLabel = QLabel("<b>{0}</b>".format(self.tr("Insert Lorem Ipsum Text")))

        self.paraLabel = QLabel(self.tr("Number of pragraphs"))
        self.paraCount = QSpinBox()
        self.paraCount.setMinimum(1)
        self.paraCount.setMaximum(100)
        self.paraCount.setValue(5)

        self.randLabel = QLabel(self.tr("Randomise order"))
        self.randSwitch = QSwitch()

        self.formBox = QGridLayout()
        self.formBox.addWidget(self.headLabel, 0, 0, 1, 2, Qt.AlignLeft)
        self.formBox.addWidget(self.paraLabel, 1, 0, 1, 1, Qt.AlignLeft)
        self.formBox.addWidget(self.paraCount, 1, 1, 1, 1, Qt.AlignRight)
        self.formBox.addWidget(self.randLabel, 2, 0, 1, 1, Qt.AlignLeft)
        self.formBox.addWidget(self.randSwitch, 2, 1, 1, 1, Qt.AlignRight)
        self.formBox.setVerticalSpacing(vSp)
        self.formBox.setRowStretch(3, 1)
        self.innerBox.addLayout(self.formBox)

        # Buttons
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.rejected.connect(self._doClose)

        self.btnClose = self.buttonBox.addButton(QDialogButtonBox.Close)
        self.btnClose.setAutoDefault(False)

        self.btnSave = self.buttonBox.addButton(self.tr("Insert"), QDialogButtonBox.ActionRole)
        self.btnSave.clicked.connect(self._doInsert)
        self.btnSave.setAutoDefault(False)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.addLayout(self.innerBox)
        self.outerBox.addWidget(self.buttonBox)
        self.outerBox.setSpacing(self.mainConf.pxInt(16))
        self.setLayout(self.outerBox)

        logger.debug("GuiLipsum initialisation complete")

        return

    ##
    #  Slots
    ##

    def _doInsert(self):
        """Load the text and insert it in the open document.
        """
        lipsumFile = os.path.join(self.mainConf.assetPath, "text", "lipsum.txt")
        lipsumText = readTextFile(lipsumFile).splitlines()

        if self.randSwitch.isChecked():
            random.shuffle(lipsumText)

        pCount = self.paraCount.value()
        inText = "\n\n".join(lipsumText[0:pCount]) + "\n\n"

        self.theParent.docEditor.insertText(inText)

        return

    def _doClose(self):
        """Close the dialog window without doing anything.
        """
        self.close()
        return

# END Class GuiLipsum

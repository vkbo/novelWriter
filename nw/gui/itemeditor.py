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

from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QGroupBox, QFormLayout, QLineEdit, QPushButton, QComboBox
from PyQt5.QtSvg     import QSvgWidget

from nw.enum         import nwItemLayout, nwItemClass, nwItemType
from nw.constants    import nwLabels

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
        self.editStatus = QComboBox()
        self.editLayout = QComboBox()

        for n in range(len(self.theProject.statusLabels)):
            self.editStatus.addItem(
                self.theProject.statusIcons[n], self.theProject.statusLabels[n], n
            )

        self.validLayouts = []
        if self.theItem.itemType == nwItemType.FILE:
            if self.theItem.itemClass == nwItemClass.NOVEL:
                self.validLayouts.append(nwItemLayout.TITLE)
                self.validLayouts.append(nwItemLayout.BOOK)
                self.validLayouts.append(nwItemLayout.PAGE)
                self.validLayouts.append(nwItemLayout.PARTITION)
                self.validLayouts.append(nwItemLayout.UNNUMBERED)
                self.validLayouts.append(nwItemLayout.CHAPTER)
                self.validLayouts.append(nwItemLayout.SCENE)
            else:
                self.validLayouts.append(nwItemLayout.NOTE)
        else:
            self.validLayouts.append(nwItemLayout.NO_LAYOUT)

        for itemLayout in nwItemLayout:
            if itemLayout in self.validLayouts:
                self.editLayout.addItem(nwLabels.LAYOUT_NAME[itemLayout],itemLayout)

        self.mainForm.addRow("Name",   self.editName)
        self.mainForm.addRow("Status", self.editStatus)
        self.mainForm.addRow("Layout", self.editLayout)

        self.editName.setMinimumWidth(200)

        self.editName.setText(self.theItem.itemName)
        statusIdx = self.editStatus.findData(self.theItem.itemStatus)
        if statusIdx != -1:
            self.editStatus.setCurrentIndex(statusIdx)
        layoutIdx = self.editLayout.findData(self.theItem.itemLayout)
        if layoutIdx != -1:
            self.editLayout.setCurrentIndex(layoutIdx)

        self.buttonBox = QHBoxLayout()
        self.closeButton = QPushButton("Close")
        self.closeButton.clicked.connect(self._doClose)
        self.saveButton = QPushButton("Save")
        self.saveButton.setDefault(True)
        self.saveButton.clicked.connect(self._doSave)
        self.buttonBox.addStretch(1)
        self.buttonBox.addWidget(self.closeButton)
        self.buttonBox.addWidget(self.saveButton)

        self.mainGroup.setLayout(self.mainForm)
        self.innerBox.addWidget(self.mainGroup)
        self.innerBox.addLayout(self.buttonBox)

        self.show()

        self.editName.selectAll()

        logger.debug("ItemEditor initialisation complete")

        return

    def _doSave(self):
        logger.verbose("ItemEditor save button clicked")
        itemName   = self.editName.text()
        itemStatus = self.editStatus.currentData()
        itemLayout = self.editLayout.currentData()
        self.theItem.setName(itemName)
        self.theItem.setStatus(itemStatus)
        self.theItem.setLayout(itemLayout)
        self.accept()
        self.close()
        return

    def _doClose(self):
        logger.verbose("ItemEditor close button clicked")
        self.reject()
        self.close()
        return

# END Class GuiItemEditor

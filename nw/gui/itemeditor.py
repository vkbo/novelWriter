# -*- coding: utf-8 -*-
"""
novelWriter – GUI Item Editor
=============================
GUI class for the item editor dialog

File History:
Created: 2019-04-27 [0.0.1]

This file is a part of novelWriter
Copyright 2018–2021, Veronica Berglyd Olsen

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

import nw
import logging

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout, QLineEdit, QComboBox, QLabel,
    QDialogButtonBox
)

from nw.gui.custom import QSwitch
from nw.constants import nwLabels, nwItemLayout, nwItemType, nwLists

logger = logging.getLogger(__name__)

class GuiItemEditor(QDialog):

    def __init__(self, theParent, theProject, tHandle):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiItemEditor ...")
        self.setObjectName("GuiItemEditor")

        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.theParent  = theParent

        ##
        #  Build GUI
        ##

        self.theItem = self.theProject.projTree[tHandle]
        if self.theItem is None:
            self._doClose()

        self.setWindowTitle("Item Settings")

        mVd = self.mainConf.pxInt(220)
        mSp = self.mainConf.pxInt(16)
        vSp = self.mainConf.pxInt(4)

        # Item Label
        self.editName = QLineEdit()
        self.editName.setMinimumWidth(mVd)
        self.editName.setMaxLength(200)

        # Item Status
        self.editStatus = QComboBox()
        self.editStatus.setMinimumWidth(mVd)
        if self.theItem.itemClass in nwLists.CLS_NOVEL:
            for sLabel, _, _ in self.theProject.statusItems:
                self.editStatus.addItem(
                    self.theParent.statusIcons[sLabel], sLabel, sLabel
                )
        else:
            for sLabel, _, _ in self.theProject.importItems:
                self.editStatus.addItem(
                    self.theParent.importIcons[sLabel], sLabel, sLabel
                )

        # Item Layout
        self.editLayout = QComboBox()
        self.editLayout.setMinimumWidth(mVd)
        validLayouts = []
        if self.theItem.itemType == nwItemType.FILE:
            if self.theItem.itemClass in nwLists.CLS_NOVEL:
                validLayouts.append(nwItemLayout.TITLE)
                validLayouts.append(nwItemLayout.BOOK)
                validLayouts.append(nwItemLayout.PAGE)
                validLayouts.append(nwItemLayout.PARTITION)
                validLayouts.append(nwItemLayout.UNNUMBERED)
                validLayouts.append(nwItemLayout.CHAPTER)
                validLayouts.append(nwItemLayout.SCENE)
            validLayouts.append(nwItemLayout.NOTE)
        else:
            validLayouts.append(nwItemLayout.NO_LAYOUT)
            self.editLayout.setEnabled(False)

        for itemLayout in nwItemLayout:
            if itemLayout in validLayouts:
                self.editLayout.addItem(nwLabels.LAYOUT_NAME[itemLayout], itemLayout)

        # Export Switch
        self.textExport = QLabel("Include when building project")
        self.editExport = QSwitch()
        if self.theItem.itemType == nwItemType.FILE:
            self.editExport.setEnabled(True)
            self.editExport.setChecked(self.theItem.isExported)
        else:
            self.editExport.setEnabled(False)
            self.editExport.setChecked(False)

        # Buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self._doSave)
        self.buttonBox.rejected.connect(self._doClose)

        # Set Current Values
        self.editName.setText(self.theItem.itemName)
        self.editName.selectAll()

        statusIdx = self.editStatus.findData(self.theItem.itemStatus)
        if statusIdx != -1:
            self.editStatus.setCurrentIndex(statusIdx)

        layoutIdx = self.editLayout.findData(self.theItem.itemLayout)
        if layoutIdx != -1:
            self.editLayout.setCurrentIndex(layoutIdx)

        ##
        #  Assemble
        ##

        self.mainForm = QGridLayout()
        self.mainForm.setVerticalSpacing(vSp)
        self.mainForm.setHorizontalSpacing(mSp)
        self.mainForm.addWidget(QLabel("Label"),  0, 0, 1, 1)
        self.mainForm.addWidget(self.editName,    0, 1, 1, 2)
        self.mainForm.addWidget(QLabel("Status"), 1, 0, 1, 1)
        self.mainForm.addWidget(self.editStatus,  1, 1, 1, 2)
        self.mainForm.addWidget(QLabel("Layout"), 2, 0, 1, 1)
        self.mainForm.addWidget(self.editLayout,  2, 1, 1, 2)
        self.mainForm.addWidget(self.textExport,  3, 0, 1, 2)
        self.mainForm.addWidget(self.editExport,  3, 2, 1, 1)
        self.mainForm.setColumnStretch(0, 0)
        self.mainForm.setColumnStretch(1, 1)
        self.mainForm.setColumnStretch(2, 0)

        self.outerBox = QVBoxLayout()
        self.outerBox.setSpacing(mSp)
        self.outerBox.addLayout(self.mainForm)
        self.outerBox.addStretch(1)
        self.outerBox.addWidget(self.buttonBox)
        self.setLayout(self.outerBox)

        self.rejected.connect(self._doClose)

        logger.debug("GuiItemEditor initialisation complete")

        return

    ##
    #  Slots
    ##

    @pyqtSlot()
    def _doSave(self):
        """Save the setting to the item.
        """
        logger.verbose("ItemEditor save button clicked")

        itemName   = self.editName.text()
        itemStatus = self.editStatus.currentData()
        itemLayout = self.editLayout.currentData()
        isExported = self.editExport.isChecked()

        self.theItem.setName(itemName)
        self.theItem.setStatus(itemStatus)
        self.theItem.setLayout(itemLayout)
        self.theItem.setExported(isExported)

        self.theProject.setProjectChanged(True)

        self.accept()
        self.close()

        return

    @pyqtSlot()
    def _doClose(self):
        """Close the dialog without saving the settings.
        """
        logger.verbose("ItemEditor cancel button clicked")
        self.close()
        return

# END Class GuiItemEditor

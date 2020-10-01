# -*- coding: utf-8 -*-
"""novelWriter GUI Item Editor

 novelWriter – GUI Item Editor
===============================
 Class holding the item editor

 File History:
 Created: 2019-04-27 [0.0.1]

 This file is a part of novelWriter
 Copyright 2018–2020, Veronica Berglyd Olsen

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

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout, QLineEdit, QComboBox, QLabel,
    QDialogButtonBox
)

from nw.gui.custom import QSwitch
from nw.constants import nwLabels, nwItemLayout, nwItemClass, nwItemType

logger = logging.getLogger(__name__)

class GuiItemEditor(QDialog):

    def __init__(self, theParent, theProject, tHandle):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiItemEditor ...")
        self.setObjectName("GuiItemEditor")

        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.theParent  = theParent

        self.outerBox = QVBoxLayout()

        self.theItem = self.theProject.projTree[tHandle]
        if self.theItem is None:
            self._doClose()

        self.setWindowTitle("Item Settings")
        self.setLayout(self.outerBox)

        # Item Label
        self.editName = QLineEdit()
        self.editName.setMinimumWidth(self.mainConf.pxInt(220))
        self.editName.setMaxLength(self.mainConf.pxInt(200))

        # Item Status
        self.editStatus = QComboBox()
        if self.theItem.itemClass == nwItemClass.NOVEL:
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
                self.validLayouts.append(nwItemLayout.NOTE)
            else:
                self.validLayouts.append(nwItemLayout.NOTE)
        else:
            self.validLayouts.append(nwItemLayout.NO_LAYOUT)

        for itemLayout in nwItemLayout:
            if itemLayout in self.validLayouts:
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

        self.editName.setText(self.theItem.itemName)
        statusIdx = self.editStatus.findData(self.theItem.itemStatus)
        if statusIdx != -1:
            self.editStatus.setCurrentIndex(statusIdx)
        layoutIdx = self.editLayout.findData(self.theItem.itemLayout)
        if layoutIdx != -1:
            self.editLayout.setCurrentIndex(layoutIdx)

        # Buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self._doSave)
        self.buttonBox.rejected.connect(self._doClose)

        # Assemble
        self.mainForm = QGridLayout()
        self.mainForm.setVerticalSpacing(4)
        self.mainForm.setHorizontalSpacing(16)
        self.mainForm.addWidget(QLabel("Label"),  0, 0, 1, 1)
        self.mainForm.addWidget(self.editName,    0, 1, 1, 2)
        self.mainForm.addWidget(QLabel("Status"), 1, 0, 1, 1)
        self.mainForm.addWidget(self.editStatus,  1, 1, 1, 2)
        self.mainForm.addWidget(QLabel("Layout"), 2, 0, 1, 1)
        self.mainForm.addWidget(self.editLayout,  2, 1, 1, 2)
        self.mainForm.addWidget(self.textExport,  3, 0, 1, 2)
        self.mainForm.addWidget(self.editExport,  3, 2, 1, 1)

        self.outerBox.setSpacing(self.mainConf.pxInt(16))
        self.outerBox.addLayout(self.mainForm)
        self.outerBox.addStretch(1)
        self.outerBox.addWidget(self.buttonBox)
        self.setLayout(self.outerBox)

        self.rejected.connect(self._doClose)
        self.editName.selectAll()

        logger.debug("GuiItemEditor initialisation complete")

        return

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

    def _doClose(self):
        """Close the dialog without saving the settings.
        """
        logger.verbose("ItemEditor close button clicked")
        self.close()
        return

# END Class GuiItemEditor

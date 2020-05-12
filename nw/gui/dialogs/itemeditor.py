# -*- coding: utf-8 -*-
"""novelWriter GUI Item Editor

 novelWriter – GUI Item Editor
===============================
 Class holding the item editor

 File History:
 Created: 2019-04-27 [0.0.1]

 This file is a part of novelWriter
 Copyright 2020, Veronica Berglyd Olsen

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

import logging
import nw

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QGroupBox, QGridLayout, QLineEdit,
    QComboBox, QLabel, QSpacerItem, QSizePolicy, QDialogButtonBox
)

from nw.gui.additions import QSwitch
from nw.constants import nwLabels, nwItemLayout, nwItemClass, nwItemType

logger = logging.getLogger(__name__)

class GuiItemEditor(QDialog):

    def __init__(self, theParent, theProject, tHandle):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiItemEditor ...")

        self.mainConf   = nw.CONFIG
        self.theProject = theProject
        self.theParent  = theParent
        self.outerBox = QHBoxLayout()
        self.innerBox = QVBoxLayout()

        self.theItem    = self.theProject.projTree[tHandle]
        if self.theItem is None:
            self._doClose()

        self.setWindowTitle("Item Settings")
        self.guiDeco = self.theParent.theTheme.loadDecoration("settings",(64,64))
        self.outerBox.setSpacing(16)

        self.setLayout(self.outerBox)
        self.outerBox.addWidget(self.guiDeco, 0, Qt.AlignTop)
        self.outerBox.addLayout(self.innerBox)

        self.mainGroup = QGroupBox("Item Settings")
        self.mainForm  = QGridLayout()

        self.editName = QLineEdit()
        self.editName.setMinimumWidth(220)
        self.editName.setMaxLength(200)

        self.editStatus = QComboBox()
        self.editLayout = QComboBox()

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
                self.editLayout.addItem(nwLabels.LAYOUT_NAME[itemLayout],itemLayout)

        self.textExport = QLabel("Include when building project")
        self.editExport = QSwitch()
        if self.theItem.itemType == nwItemType.FILE:
            self.editExport.setEnabled(True)
            self.editExport.setChecked(self.theItem.isExported)
        else:
            self.editExport.setEnabled(False)
            self.editExport.setChecked(False)

        self.mainForm.addWidget(QLabel("Label"),  0, 0)
        self.mainForm.addWidget(self.editName,    0, 1, 1, 2)
        self.mainForm.addWidget(QLabel("Status"), 1, 0)
        self.mainForm.addWidget(self.editStatus,  1, 1, 1, 2)
        self.mainForm.addWidget(QLabel("Layout"), 2, 0)
        self.mainForm.addWidget(self.editLayout,  2, 1, 1, 2)
        self.mainForm.addWidget(self.textExport,  4, 0, 1, 2)
        self.mainForm.addWidget(self.editExport,  4, 2)

        self.spacerItem = QSpacerItem(12, 12, QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.mainForm.addItem(self.spacerItem,  3, 0)

        self.editName.setText(self.theItem.itemName)
        statusIdx = self.editStatus.findData(self.theItem.itemStatus)
        if statusIdx != -1:
            self.editStatus.setCurrentIndex(statusIdx)
        layoutIdx = self.editLayout.findData(self.theItem.itemLayout)
        if layoutIdx != -1:
            self.editLayout.setCurrentIndex(layoutIdx)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self._doSave)
        self.buttonBox.rejected.connect(self._doClose)

        self.mainGroup.setLayout(self.mainForm)
        self.innerBox.addWidget(self.mainGroup)
        self.innerBox.addWidget(self.buttonBox)

        self.show()

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
        logger.verbose("ItemEditor close button clicked")
        self.reject()
        self.close()
        return

# END Class GuiItemEditor

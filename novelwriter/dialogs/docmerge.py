"""
novelWriter – GUI Doc Merge Dialog
==================================
Custom dialog class for merging documents.

File History:
Created:   2020-01-23 [0.4.3]
Rewritten: 2022-10-06 [2.0rc1]

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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
import novelwriter

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QAbstractItemView, QDialog, QDialogButtonBox, QGridLayout, QLabel,
    QListWidget, QListWidgetItem, QVBoxLayout,
)

from novelwriter.custom import QHelpLabel, QSwitch

logger = logging.getLogger(__name__)


class GuiDocMerge(QDialog):

    def __init__(self, mainGui, sHandle, itemList):
        super().__init__(parent=mainGui)

        logger.debug("Initialising GuiDocMerge ...")
        self.setObjectName("GuiDocMerge")

        self.mainConf   = novelwriter.CONFIG
        self.mainGui    = mainGui
        self.mainTheme  = mainGui.mainTheme
        self.theProject = mainGui.theProject

        self._data = {}

        self.setWindowTitle(self.tr("Merge Documents"))

        self.headLabel = QLabel("<b>{0}</b>".format(self.tr("Documents to Merge")))
        self.helpLabel = QHelpLabel(self.tr(
            "Drag and drop items to change the order, or uncheck to exclude."
        ), self.mainTheme.helpText)

        iPx = self.mainTheme.baseIconSize
        hSp = self.mainConf.pxInt(12)
        vSp = self.mainConf.pxInt(8)
        bSp = self.mainConf.pxInt(12)

        self.listBox = QListWidget()
        self.listBox.setIconSize(QSize(iPx, iPx))
        self.listBox.setMinimumWidth(self.mainConf.pxInt(400))
        self.listBox.setMinimumHeight(self.mainConf.pxInt(180))
        self.listBox.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.listBox.setSelectionMode(QAbstractItemView.SingleSelection)
        self.listBox.setDragDropMode(QAbstractItemView.InternalMove)

        # Merge Options
        self.trashLabel = QLabel(self.tr("Move merged items to Trash"))
        self.trashSwitch = QSwitch(width=2*iPx, height=iPx)

        self.optBox = QGridLayout()
        self.optBox.addWidget(self.trashLabel,  0, 0)
        self.optBox.addWidget(self.trashSwitch, 0, 1)
        self.optBox.setHorizontalSpacing(hSp)
        self.optBox.setColumnStretch(2, 1)

        # Buttons
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.resetButton = self.buttonBox.addButton(QDialogButtonBox.Reset)
        self.resetButton.clicked.connect(self._resetList)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.setSpacing(0)
        self.outerBox.addWidget(self.headLabel)
        self.outerBox.addWidget(self.helpLabel)
        self.outerBox.addSpacing(vSp)
        self.outerBox.addWidget(self.listBox)
        self.outerBox.addSpacing(vSp)
        self.outerBox.addLayout(self.optBox)
        self.outerBox.addSpacing(bSp)
        self.outerBox.addWidget(self.buttonBox)
        self.setLayout(self.outerBox)

        # Load Content
        self._loadContent(sHandle, itemList)

        logger.debug("GuiDocMerge initialisation complete")

        return

    def getData(self):
        """Return the user's choices.
        """
        finalItems = []
        for i in range(self.listBox.count()):
            item = self.listBox.item(i)
            if item is not None and item.checkState() == Qt.Checked:
                finalItems.append(item.data(Qt.UserRole))

        self._data["moveToTrash"] = self.trashSwitch.isChecked()
        self._data["finalItems"] = finalItems

        return self._data

    ##
    #  Slots
    ##

    def _resetList(self):
        """Reset the content of the list box to its original state.
        """
        logger.debug("Resetting list box content")
        sHandle = self._data.get("sHandle", None)
        itemList = self._data.get("origItems", [])
        self._loadContent(sHandle, itemList)
        return

    ##
    #  Internal Functions
    ##

    def _loadContent(self, sHandle, itemList):
        """Load content from a given list of items.
        """
        self._data = {}
        self._data["sHandle"] = sHandle
        self._data["origItems"] = itemList

        self.listBox.clear()
        for tHandle in itemList:
            nwItem = self.theProject.tree[tHandle]
            if nwItem is None or not nwItem.isFileType():
                continue

            itemIcon = self.mainTheme.getItemIcon(
                nwItem.itemType, nwItem.itemClass, nwItem.itemLayout, nwItem.mainHeading
            )

            newItem = QListWidgetItem()
            newItem.setIcon(itemIcon)
            newItem.setText(nwItem.itemName)
            newItem.setData(Qt.UserRole, tHandle)
            newItem.setCheckState(Qt.Checked)

            self.listBox.addItem(newItem)

        return

# END Class GuiDocMerge

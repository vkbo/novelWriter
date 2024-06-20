"""
novelWriter – GUI Doc Split Dialog
==================================

File History:
Created:   2020-02-01 [0.4.3]  GuiDocSplit
Rewritten: 2022-10-12 [2.0rc1] GuiDocSplit

This file is a part of novelWriter
Copyright 2018–2024, Veronica Berglyd Olsen

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
from __future__ import annotations

import logging

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (
    QAbstractItemView, QComboBox, QDialogButtonBox, QGridLayout, QLabel,
    QListWidget, QListWidgetItem, QVBoxLayout, QWidget
)

from novelwriter import CONFIG, SHARED
from novelwriter.extensions.configlayout import NColourLabel
from novelwriter.extensions.modified import NDialog
from novelwriter.extensions.switch import NSwitch
from novelwriter.types import QtAccepted, QtDialogCancel, QtDialogOk, QtUserRole

logger = logging.getLogger(__name__)


class GuiDocSplit(NDialog):

    LINE_ROLE  = QtUserRole
    LEVEL_ROLE = QtUserRole + 1
    LABEL_ROLE = QtUserRole + 2

    def __init__(self, parent: QWidget, sHandle: str) -> None:
        super().__init__(parent=parent)

        logger.debug("Create: GuiDocSplit")
        self.setObjectName("GuiDocSplit")

        self._data = {}
        self._text = []

        self.setWindowTitle(self.tr("Split Document"))

        self.headLabel = QLabel(self.tr("Document Headings"), self)
        self.headLabel.setFont(SHARED.theme.guiFontB)
        self.helpLabel = NColourLabel(
            self.tr("Select the maximum level to split into files."),
            self, color=SHARED.theme.helpText, wrap=True
        )

        # Values
        iPx = SHARED.theme.baseIconHeight
        hSp = CONFIG.pxInt(12)
        vSp = CONFIG.pxInt(8)
        bSp = CONFIG.pxInt(12)

        pOptions = SHARED.project.options
        spLevel = pOptions.getInt("GuiDocSplit", "spLevel", 3)
        intoFolder = pOptions.getBool("GuiDocSplit", "intoFolder", True)
        docHierarchy = pOptions.getBool("GuiDocSplit", "docHierarchy", True)

        # Heading Selection
        self.listBox = QListWidget(self)
        self.listBox.setDragDropMode(QAbstractItemView.DragDropMode.NoDragDrop)
        self.listBox.setMinimumWidth(CONFIG.pxInt(400))
        self.listBox.setMinimumHeight(CONFIG.pxInt(180))

        self.splitLevel = QComboBox(self)
        self.splitLevel.addItem(self.tr("Split on Heading Level 1 (Partition)"),      1)
        self.splitLevel.addItem(self.tr("Split up to Heading Level 2 (Chapter)"), 2)
        self.splitLevel.addItem(self.tr("Split up to Heading Level 3 (Scene)"),   3)
        self.splitLevel.addItem(self.tr("Split up to Heading Level 4 (Section)"), 4)
        spIndex = self.splitLevel.findData(spLevel)
        if spIndex != -1:
            self.splitLevel.setCurrentIndex(spIndex)
        self.splitLevel.currentIndexChanged.connect(self._reloadList)

        # Split Options
        self.folderLabel = QLabel(self.tr("Split into a new folder"), self)
        self.folderSwitch = NSwitch(self, height=iPx)
        self.folderSwitch.setChecked(intoFolder)

        self.hierarchyLabel = QLabel(self.tr("Create document hierarchy"), self)
        self.hierarchySwitch = NSwitch(self, height=iPx)
        self.hierarchySwitch.setChecked(docHierarchy)

        self.trashLabel = QLabel(self.tr("Move split document to Trash"), self)
        self.trashSwitch = NSwitch(self, height=iPx)

        self.optBox = QGridLayout()
        self.optBox.addWidget(self.folderLabel,  0, 0)
        self.optBox.addWidget(self.folderSwitch, 0, 1)
        self.optBox.addWidget(self.hierarchyLabel,  1, 0)
        self.optBox.addWidget(self.hierarchySwitch, 1, 1)
        self.optBox.addWidget(self.trashLabel,  2, 0)
        self.optBox.addWidget(self.trashSwitch, 2, 1)
        self.optBox.setVerticalSpacing(vSp)
        self.optBox.setHorizontalSpacing(hSp)
        self.optBox.setColumnStretch(3, 1)

        # Buttons
        self.buttonBox = QDialogButtonBox(QtDialogOk | QtDialogCancel, self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # Assemble
        self.outerBox = QVBoxLayout()
        self.outerBox.setSpacing(0)
        self.outerBox.addWidget(self.headLabel)
        self.outerBox.addWidget(self.helpLabel)
        self.outerBox.addSpacing(vSp)
        self.outerBox.addWidget(self.listBox)
        self.outerBox.addWidget(self.splitLevel)
        self.outerBox.addSpacing(vSp)
        self.outerBox.addLayout(self.optBox)
        self.outerBox.addSpacing(bSp)
        self.outerBox.addWidget(self.buttonBox)
        self.setLayout(self.outerBox)

        # Load Content
        self._loadContent(sHandle)

        logger.debug("Ready: GuiDocSplit")

        return

    def __del__(self) -> None:  # pragma: no cover
        logger.debug("Delete: GuiDocSplit")
        return

    def data(self) -> tuple[dict, list[str]]:
        """Return the user's choices. Also save the users options for
        the next time the dialog is used.
        """
        headerList = []
        for i in range(self.listBox.count()):
            item = self.listBox.item(i)
            if item is not None:
                headerList.append((
                    item.data(self.LINE_ROLE),
                    item.data(self.LEVEL_ROLE),
                    item.data(self.LABEL_ROLE),
                ))

        spLevel = self.splitLevel.currentData()
        intoFolder = self.folderSwitch.isChecked()
        docHierarchy = self.hierarchySwitch.isChecked()
        moveToTrash = self.trashSwitch.isChecked()

        self._data["spLevel"] = spLevel
        self._data["headerList"] = headerList
        self._data["intoFolder"] = intoFolder
        self._data["docHierarchy"] = docHierarchy
        self._data["moveToTrash"] = moveToTrash

        logger.debug("Saving State: GuiDocSplit")
        pOptions = SHARED.project.options
        pOptions.setValue("GuiDocSplit", "spLevel", spLevel)
        pOptions.setValue("GuiDocSplit", "intoFolder", intoFolder)
        pOptions.setValue("GuiDocSplit", "docHierarchy", docHierarchy)

        return self._data, self._text

    @classmethod
    def getData(cls, parent: QWidget, handle: str) -> tuple[dict, list[str], bool]:
        """Pop the dialog and return the result."""
        cls = GuiDocSplit(parent, handle)
        cls.exec()
        data, text = cls.data()
        accepted = cls.result() == QtAccepted
        cls.softDelete()
        return data, text, accepted

    ##
    #  Private Slots
    ##

    @pyqtSlot()
    def _reloadList(self) -> None:
        """Reload the content of the list box."""
        sHandle = self._data.get("sHandle", None)
        self._loadContent(sHandle)
        return

    ##
    #  Internal Functions
    ##

    def _loadContent(self, sHandle: str) -> None:
        """Load content from a given source item."""
        self._data = {}
        self._data["sHandle"] = sHandle

        self.listBox.clear()

        nwItem = SHARED.project.tree[sHandle]
        if nwItem is None or not nwItem.isFileType():
            return

        spLevel = self.splitLevel.currentData()
        if not self._text:
            self._text = SHARED.project.storage.getDocumentText(sHandle).splitlines()

        for lineNo, aLine in enumerate(self._text):

            onLine = -1
            hLevel = 0
            hLabel = aLine.strip()
            if aLine.startswith("# ") and spLevel >= 1:
                onLine = lineNo
                hLevel = 1
                hLabel = aLine[2:].strip()
            elif aLine.startswith("## ") and spLevel >= 2:
                onLine = lineNo
                hLevel = 2
                hLabel = aLine[3:].strip()
            elif aLine.startswith("### ") and spLevel >= 3:
                onLine = lineNo
                hLevel = 3
                hLabel = aLine[4:].strip()
            elif aLine.startswith("#### ") and spLevel >= 4:
                onLine = lineNo
                hLevel = 4
                hLabel = aLine[5:].strip()
            elif aLine.startswith("#! ") and spLevel >= 1:
                onLine = lineNo
                hLevel = 1
                hLabel = aLine[3:].strip()
            elif aLine.startswith("##! ") and spLevel >= 2:
                onLine = lineNo
                hLevel = 2
                hLabel = aLine[4:].strip()

            if onLine >= 0 and hLevel > 0:
                newItem = QListWidgetItem()
                newItem.setText(aLine.strip())
                newItem.setData(self.LINE_ROLE, onLine)
                newItem.setData(self.LEVEL_ROLE, hLevel)
                newItem.setData(self.LABEL_ROLE, hLabel)
                self.listBox.addItem(newItem)

        return

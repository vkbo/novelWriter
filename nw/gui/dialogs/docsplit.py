# -*- coding: utf-8 -*-
"""novelWriter GUI Doc Split

 novelWriter – GUI Doc Split
=============================
 Tool for splitting a single document into multiple documents

 File History:
 Created: 2020-02-01 [0.4.3]

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
    QDialog, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, QComboBox,
    QListWidget, QAbstractItemView, QListWidgetItem
)
from nw.constants import nwAlert, nwItemType, nwItemClass, nwItemLayout
from nw.core import NWDoc

logger = logging.getLogger(__name__)

class GuiDocSplit(QDialog):

    def __init__(self, theParent, theProject):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiDocSplit ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
        self.optState   = self.theProject.optState
        self.sourceItem = None

        self.outerBox = QHBoxLayout()
        self.innerBox = QVBoxLayout()
        self.setWindowTitle("Split Document")
        self.setLayout(self.outerBox)

        self.guiDeco = self.theParent.theTheme.loadDecoration("split",(64,64))

        self.outerBox.addWidget(self.guiDeco, 0, Qt.AlignTop)
        self.outerBox.addLayout(self.innerBox)

        self.doMergeForm = QGridLayout()
        self.doMergeForm.setContentsMargins(0,0,0,0)

        self.listBox = QListWidget()
        self.listBox.setDragDropMode(QAbstractItemView.NoDragDrop)

        self.splitLevel = QComboBox(self)
        self.splitLevel.addItem("Split on Header Level 1 (Title)",      1)
        self.splitLevel.addItem("Split up to Header Level 2 (Chapter)", 2)
        self.splitLevel.addItem("Split up to Header Level 3 (Scene)",   3)
        self.splitLevel.addItem("Split up to Header Level 4 (Section)", 4)
        spIndex = self.splitLevel.findData(
            self.optState.getInt("GuiDocSplit", "spLevel", 3)
        )
        if spIndex != -1:
            self.splitLevel.setCurrentIndex(spIndex)
        self.splitLevel.currentIndexChanged.connect(self._populateList)

        self.splitButton = QPushButton("Split")
        self.splitButton.clicked.connect(self._doSplit)

        self.closeButton = QPushButton("Close")
        self.closeButton.clicked.connect(self._doClose)

        self.doMergeForm.addWidget(self.listBox,     0, 0, 1, 3)
        self.doMergeForm.addWidget(self.splitLevel,  1, 0, 1, 3)
        self.doMergeForm.addWidget(self.splitButton, 2, 1)
        self.doMergeForm.addWidget(self.closeButton, 2, 2)

        self.innerBox.addLayout(self.doMergeForm)

        self.rejected.connect(self._doClose)
        self.show()

        self._populateList()

        logger.debug("GuiDocSplit initialisation complete")

        return

    ##
    #  Buttons
    ##

    def _doSplit(self):
        """Perform the split of the file, create a new folder in the
        same parent folder, and multiple files depending on split level
        settings. The old file is not removed in the merge process, and
        must be deleted manually.
        """

        logger.verbose("GuiDocSplit split button clicked")

        if self.sourceItem is None:
            self.theParent.makeAlert((
                "No source document selected. Nothing to do."
            ), nwAlert.ERROR)
            return

        srcItem = self.theProject.projTree[self.sourceItem]
        if srcItem is None:
            self.theParent.makeAlert((
                "Could not parse source document."
            ), nwAlert.ERROR)
            return

        theDoc   = NWDoc(self.theProject, self.theParent)
        theText  = theDoc.openDocument(self.sourceItem, False)
        theLines = theText.splitlines()
        nLines   = len(theLines)
        theLines.insert(0, "%Split Doc")
        logger.debug(
            "Splitting document %s with %d lines" % (self.sourceItem,nLines)
        )

        finalOrder = []
        for i in range(self.listBox.count()):
            listItem = self.listBox.item(i)
            wTitle = listItem.text()
            lineNo = listItem.data(Qt.UserRole)
            finalOrder.append([wTitle, lineNo, nLines])
            if i > 0:
                finalOrder[i-1][2] = lineNo

        if len(finalOrder) == 0:
            self.theParent.makeAlert((
                "No headers found. Nothing to do."
            ), nwAlert.ERROR)
            return

        fHandle = self.theProject.newFolder(srcItem.itemName, srcItem.itemClass, srcItem.parHandle)
        self.theParent.treeView.revealTreeItem(fHandle)
        logger.verbose("Creating folder %s" % fHandle)

        for wTitle, iStart, iEnd in finalOrder:

            itemLayout = nwItemLayout.NOTE
            if srcItem.itemClass == nwItemClass.NOVEL:
                if wTitle.startswith("# "):
                    itemLayout = nwItemLayout.PARTITION
                elif wTitle.startswith("## "):
                    itemLayout = nwItemLayout.CHAPTER
                elif wTitle.startswith("### "):
                    itemLayout = nwItemLayout.SCENE
                elif wTitle.startswith("#### "):
                    itemLayout = nwItemLayout.PAGE

            wTitle = wTitle.lstrip("#")
            wTitle = wTitle.strip()

            nHandle = self.theProject.newFile(wTitle, srcItem.itemClass, fHandle)
            newItem = self.theProject.projTree[nHandle]
            newItem.setLayout(itemLayout)
            logger.verbose(
                "Creating new document %s with text from line %d to %d" % (nHandle, iStart, iEnd-1)
            )

            theText = "\n".join(theLines[iStart:iEnd])
            theDoc.openDocument(nHandle, False)
            theDoc.saveDocument(theText)
            theDoc.clearDocument()
            self.theParent.treeView.revealTreeItem(nHandle)

        self.close()

        return

    def _doClose(self):
        """Close the dialog window without doing anything.
        """
        logger.verbose("GuiDocSplit close button clicked")
        self.optState.saveSettings()
        self.close()
        return

    ##
    #  Internal Functions
    ##

    def _populateList(self):
        """Get the item selected in the tree, check that it is a folder,
        and try to find all files associated with it. The valid files
        are then added to the list view in order. The list itself can be
        reordered by the user.
        """

        if self.sourceItem is None:
            self.sourceItem = self.theParent.treeView.getSelectedHandle()

        if self.sourceItem is None:
            return

        nwItem = self.theProject.projTree[self.sourceItem]
        if nwItem is None:
            return
        if nwItem.itemType is not nwItemType.FILE:
            self.theParent.makeAlert((
                "Element selected in the project tree must be a file."
            ), nwAlert.ERROR)
            return

        self.listBox.clear()
        theDoc  = NWDoc(self.theProject, self.theParent)
        theText = theDoc.openDocument(self.sourceItem, False)

        spLevel = self.splitLevel.currentData()
        self.optState.setValue("GuiDocSplit", "spLevel", spLevel)
        logger.debug("Scanning document %s for headings level <= %d" % (self.sourceItem, spLevel))

        lineNo = 0
        for aLine in theText.splitlines():

            lineNo += 1
            onLine  = 0

            if aLine.startswith("# ") and spLevel >= 1:
                onLine = lineNo
            elif aLine.startswith("## ") and spLevel >= 2:
                onLine = lineNo
            elif aLine.startswith("### ") and spLevel >= 3:
                onLine = lineNo
            elif aLine.startswith("#### ") and spLevel >= 4:
                onLine = lineNo

            if onLine > 0:
                newItem = QListWidgetItem()
                newItem.setText(aLine.strip())
                newItem.setData(Qt.UserRole, onLine)
                self.listBox.addItem(newItem)

        return

# END Class GuiDocSplit

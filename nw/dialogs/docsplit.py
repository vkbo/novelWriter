"""
novelWriter – GUI Doc Split Tool
================================
GUI class for splitting a single document into multiple documents

File History:
Created: 2020-02-01 [0.4.3]

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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QComboBox, QListWidget, QAbstractItemView,
    QListWidgetItem, QDialogButtonBox, QLabel
)

from nw.core import NWDoc
from nw.enum import nwAlert, nwItemType, nwItemClass, nwItemLayout
from nw.constants import nwConst
from nw.gui.custom import QHelpLabel

logger = logging.getLogger(__name__)


class GuiDocSplit(QDialog):

    def __init__(self, theParent):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiDocSplit ...")
        self.setObjectName("GuiDocSplit")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theParent.theProject
        self.optState   = theParent.theProject.optState

        self.sourceItem = None
        self.sourceText = []

        self.outerBox = QVBoxLayout()
        self.setWindowTitle(self.tr("Split Document"))

        self.headLabel = QLabel("<b>%s</b>" % self.tr("Document Headers"))
        self.helpLabel = QHelpLabel(
            self.tr("Select the maximum level to split into files."),
            self.theParent.theTheme.helpText
        )

        self.listBox = QListWidget()
        self.listBox.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.listBox.setMinimumWidth(self.mainConf.pxInt(400))
        self.listBox.setMinimumHeight(self.mainConf.pxInt(180))

        self.splitLevel = QComboBox(self)
        self.splitLevel.addItem(self.tr("Split on Header Level 1 (Title)"),      1)
        self.splitLevel.addItem(self.tr("Split up to Header Level 2 (Chapter)"), 2)
        self.splitLevel.addItem(self.tr("Split up to Header Level 3 (Scene)"),   3)
        self.splitLevel.addItem(self.tr("Split up to Header Level 4 (Section)"), 4)
        spIndex = self.splitLevel.findData(
            self.optState.getInt("GuiDocSplit", "spLevel", 3)
        )
        if spIndex != -1:
            self.splitLevel.setCurrentIndex(spIndex)
        self.splitLevel.currentIndexChanged.connect(self._populateList)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self._doSplit)
        self.buttonBox.rejected.connect(self._doClose)

        self.outerBox.setSpacing(0)
        self.outerBox.addWidget(self.headLabel)
        self.outerBox.addWidget(self.helpLabel)
        self.outerBox.addSpacing(self.mainConf.pxInt(8))
        self.outerBox.addWidget(self.listBox)
        self.outerBox.addWidget(self.splitLevel)
        self.outerBox.addSpacing(self.mainConf.pxInt(12))
        self.outerBox.addWidget(self.buttonBox)
        self.setLayout(self.outerBox)

        self.rejected.connect(self._doClose)

        self._populateList()

        logger.debug("GuiDocSplit initialisation complete")

        return

    ##
    #  Buttons
    ##

    def _doSplit(self):
        """Perform the split of the file, create a new folder in the
        same parent folder, and multiple files depending on split level
        settings. The old file is not removed in the split process, and
        must be deleted manually.
        """
        logger.verbose("GuiDocSplit split button clicked")

        if self.sourceItem is None:
            self.theParent.makeAlert(self.tr(
                "No source document selected. Nothing to do."
            ), nwAlert.ERROR)
            return False

        srcItem = self.theProject.projTree[self.sourceItem]
        if srcItem is None:
            self.theParent.makeAlert(self.tr(
                "Could not parse source document."
            ), nwAlert.ERROR)
            return False

        inDoc = NWDoc(self.theProject, self.sourceItem)
        theText = inDoc.readDocument()

        docErr = inDoc.getError()
        if theText is None and docErr:
            self.theParent.makeAlert([
                self.tr("Failed to open document file."), docErr
            ], nwAlert.ERROR)

        if theText is None:
            theText = ""

        nLines = len(self.sourceText)
        logger.debug(
            "Splitting document %s with %d lines" % (self.sourceItem, nLines)
        )

        finalOrder = []
        for i in range(self.listBox.count()):
            listItem = self.listBox.item(i)
            wTitle = listItem.text()
            lineNo = listItem.data(Qt.UserRole)
            finalOrder.append([wTitle, lineNo, nLines])
            if i > 0:
                finalOrder[i-1][2] = lineNo

        nFiles = len(finalOrder)
        if nFiles == 0:
            self.theParent.makeAlert(self.tr(
                "No headers found. Nothing to do."
            ), nwAlert.ERROR)
            return False

        # Check that another folder can be created
        parTree = self.theProject.projTree.getItemPath(srcItem.itemParent)
        if len(parTree) >= nwConst.MAX_DEPTH - 1:
            self.theParent.makeAlert(self.tr(
                "Cannot add new folder for the document split. "
                "Maximum folder depth has been reached. "
                "Please move the file to another level in the project tree."
            ), nwAlert.ERROR)
            return False

        msgYes = self.theParent.askQuestion(
            self.tr("Split Document"),
            "%s<br><br>%s" % (
                self.tr(
                    "The document will be split into {0} file(s) in a new folder. "
                    "The original document will remain intact.").format(nFiles),
                self.tr(
                    "Continue with the splitting process?"
                )
            )
        )
        if not msgYes:
            return False

        # Create the folder
        fHandle = self.theProject.newFolder(
            srcItem.itemName, srcItem.itemClass, srcItem.itemParent
        )
        self.theParent.treeView.revealNewTreeItem(fHandle)
        logger.verbose("Creating folder '%s'", fHandle)

        # Loop through, and create the files
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
                    itemLayout = nwItemLayout.SCENE

            wTitle = wTitle.lstrip("#")
            wTitle = wTitle.strip()

            nHandle = self.theProject.newFile(wTitle, srcItem.itemClass, fHandle)
            newItem = self.theProject.projTree[nHandle]
            newItem.setLayout(itemLayout)
            newItem.setStatus(srcItem.itemStatus)
            logger.verbose(
                "Creating new document %s with text from line %d to %d" % (
                    nHandle, iStart+1, iEnd
                )
            )

            theText = "\n".join(self.sourceText[iStart:iEnd])
            theText = theText.rstrip("\n") + "\n\n"

            outDoc = NWDoc(self.theProject, nHandle)
            if not outDoc.writeDocument(theText):
                self.theParent.makeAlert([
                    self.tr("Could not save document."), outDoc.getError()
                ], nwAlert.ERROR)
                return False

            self.theParent.treeView.revealNewTreeItem(nHandle)

        self._doClose()

        return True

    def _doClose(self):
        """Close the dialog window without doing anything.
        """
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
        self.listBox.clear()
        if self.sourceItem is None:
            self.sourceItem = self.theParent.treeView.getSelectedHandle()

        if self.sourceItem is None:
            return False

        nwItem = self.theProject.projTree[self.sourceItem]
        if nwItem is None:
            return False

        if nwItem.itemType is not nwItemType.FILE:
            self.theParent.makeAlert(self.tr(
                "Element selected in the project tree must be a file."
            ), nwAlert.ERROR)
            return False

        inDoc = NWDoc(self.theProject, self.sourceItem)
        theText = inDoc.readDocument()
        if theText is None:
            theText = ""
            return False

        spLevel = self.splitLevel.currentData()
        self.optState.setValue("GuiDocSplit", "spLevel", spLevel)
        logger.debug(
            "Scanning document %s for headings level <= %d" % (self.sourceItem, spLevel)
        )

        self.sourceText = theText.splitlines()
        for lineNo, aLine in enumerate(self.sourceText):

            onLine = -1
            if aLine.startswith("# ") and spLevel >= 1:
                onLine = lineNo
            elif aLine.startswith("## ") and spLevel >= 2:
                onLine = lineNo
            elif aLine.startswith("### ") and spLevel >= 3:
                onLine = lineNo
            elif aLine.startswith("#### ") and spLevel >= 4:
                onLine = lineNo

            if onLine >= 0:
                newItem = QListWidgetItem()
                newItem.setText(aLine.strip())
                newItem.setData(Qt.UserRole, onLine)
                self.listBox.addItem(newItem)

        return True

# END Class GuiDocSplit

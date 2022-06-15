"""
novelWriter – GUI Doc Split Tool
================================
GUI class for splitting a single document into multiple documents

File History:
Created: 2020-02-01 [0.4.3]

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

import logging
import novelwriter

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QComboBox, QListWidget, QAbstractItemView,
    QListWidgetItem, QDialogButtonBox, QLabel
)

from novelwriter.core import NWDoc
from novelwriter.enum import nwAlert, nwItemType
from novelwriter.gui.custom import QHelpLabel

logger = logging.getLogger(__name__)


class GuiDocSplit(QDialog):

    def __init__(self, mainGui):
        QDialog.__init__(self, mainGui)

        logger.debug("Initialising GuiDocSplit ...")
        self.setObjectName("GuiDocSplit")

        self.mainConf   = novelwriter.CONFIG
        self.mainGui    = mainGui
        self.theProject = mainGui.theProject

        self.sourceItem = None
        self.sourceText = []

        self.outerBox = QVBoxLayout()
        self.setWindowTitle(self.tr("Split Document"))

        self.headLabel = QLabel("<b>{0}</b>".format(self.tr("Document Headers")))
        self.helpLabel = QHelpLabel(
            self.tr("Select the maximum level to split into files."),
            self.mainGui.mainTheme.helpText
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
            self.theProject.options.getInt("GuiDocSplit", "spLevel", 3)
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
            self.mainGui.makeAlert(self.tr(
                "No source document selected. Nothing to do."
            ), nwAlert.ERROR)
            return False

        srcItem = self.theProject.tree[self.sourceItem]
        if srcItem is None:
            self.mainGui.makeAlert(self.tr(
                "Could not parse source document."
            ), nwAlert.ERROR)
            return False

        inDoc = NWDoc(self.theProject, self.sourceItem)
        theText = inDoc.readDocument()

        docErr = inDoc.getError()
        if theText is None and docErr:
            self.mainGui.makeAlert([
                self.tr("Failed to open document file."), docErr
            ], nwAlert.ERROR)

        if theText is None:
            theText = ""

        nLines = len(self.sourceText)
        logger.debug("Splitting document %s with %d lines", self.sourceItem, nLines)

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
            self.mainGui.makeAlert(self.tr(
                "No headers found. Nothing to do."
            ), nwAlert.ERROR)
            return False

        msgYes = self.mainGui.askQuestion(
            self.tr("Split Document"),
            "{0}<br><br>{1}".format(
                self.tr(
                    "The document will be split into {0} file(s) in a new folder. "
                    "The original document will remain intact."
                ).format(nFiles),
                self.tr(
                    "Continue with the splitting process?"
                )
            )
        )
        if not msgYes:
            return False

        # Create the folder
        fHandle = self.theProject.newFolder(srcItem.itemName, srcItem.itemParent)
        self.mainGui.projView.revealNewTreeItem(fHandle)
        logger.verbose("Creating folder '%s'", fHandle)

        # Loop through, and create the files
        for wTitle, iStart, iEnd in finalOrder:

            wTitle = wTitle.lstrip("#").strip()
            nHandle = self.theProject.newFile(wTitle, fHandle)
            newItem = self.theProject.tree[nHandle]
            newItem.setStatus(srcItem.itemStatus)
            newItem.setImport(srcItem.itemImport)
            logger.verbose(
                "Creating new document '%s' with text from line %d to %d",
                nHandle, iStart+1, iEnd
            )

            theText = "\n".join(self.sourceText[iStart:iEnd])
            theText = theText.rstrip("\n") + "\n\n"

            outDoc = NWDoc(self.theProject, nHandle)
            if not outDoc.writeDocument(theText):
                self.mainGui.makeAlert([
                    self.tr("Could not save document."), outDoc.getError()
                ], nwAlert.ERROR)
                return False

            self.mainGui.projView.revealNewTreeItem(nHandle)

        self._doClose()

        return True

    def _doClose(self):
        """Close the dialog window without doing anything.
        """
        self.theProject.options.saveSettings()
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
            self.sourceItem = self.mainGui.projView.getSelectedHandle()

        if self.sourceItem is None:
            return False

        nwItem = self.theProject.tree[self.sourceItem]
        if nwItem is None:
            return False

        if nwItem.itemType is not nwItemType.FILE:
            self.mainGui.makeAlert(self.tr(
                "Element selected in the project tree must be a file."
            ), nwAlert.ERROR)
            return False

        inDoc = NWDoc(self.theProject, self.sourceItem)
        theText = inDoc.readDocument()
        if theText is None:
            theText = ""
            return False

        spLevel = self.splitLevel.currentData()
        self.theProject.options.setValue("GuiDocSplit", "spLevel", spLevel)
        logger.debug(
            "Scanning document '%s' for headings level <= %d",
            self.sourceItem, spLevel
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

# -*- coding: utf-8 -*-
"""
novelWriter – GUI Doc Merge Tool
================================
GUI class for merging multiple documents to one document

File History:
Created: 2020-01-23 [0.4.3]

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
    QDialog, QVBoxLayout, QLabel, QListWidget, QAbstractItemView,
    QListWidgetItem, QDialogButtonBox
)

from nw.core import NWDoc
from nw.enum import nwAlert, nwItemType
from nw.gui.custom import QHelpLabel

logger = logging.getLogger(__name__)

class GuiDocMerge(QDialog):

    def __init__(self, theParent, theProject):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiDocMerge ...")
        self.setObjectName("GuiDocMerge")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
        self.sourceItem = None

        self.outerBox = QVBoxLayout()
        self.setWindowTitle(self.tr("Merge Documents"))

        self.headLabel = QLabel("<b>%s</b>" % self.tr("Documents to Merge"))
        self.helpLabel = QHelpLabel(
            self.tr("Drag and drop items to change the order."), self.theParent.theTheme.helpText
        )

        self.listBox = QListWidget()
        self.listBox.setDragDropMode(QAbstractItemView.InternalMove)
        self.listBox.setMinimumWidth(self.mainConf.pxInt(400))
        self.listBox.setMinimumHeight(self.mainConf.pxInt(180))

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self._doMerge)
        self.buttonBox.rejected.connect(self._doClose)

        self.outerBox.setSpacing(0)
        self.outerBox.addWidget(self.headLabel)
        self.outerBox.addWidget(self.helpLabel)
        self.outerBox.addSpacing(self.mainConf.pxInt(8))
        self.outerBox.addWidget(self.listBox)
        self.outerBox.addSpacing(self.mainConf.pxInt(12))
        self.outerBox.addWidget(self.buttonBox)
        self.setLayout(self.outerBox)

        self.rejected.connect(self._doClose)

        self._populateList()

        logger.debug("GuiDocMerge initialisation complete")

        return

    ##
    #  Buttons
    ##

    def _doMerge(self):
        """Perform the merge of the files in the selected folder, and
        create a new file in the same parent folder. The old files are
        not removed in the merge process, and must be deleted manually.
        """
        logger.verbose("GuiDocMerge merge button clicked")

        finalOrder = []
        for i in range(self.listBox.count()):
            finalOrder.append(self.listBox.item(i).data(Qt.UserRole))

        if len(finalOrder) == 0:
            self.theParent.makeAlert(
                self.tr("No source documents found. Nothing to do."), nwAlert.ERROR
            )
            return

        theDoc = NWDoc(self.theProject, self.theParent)
        theText = ""
        for tHandle in finalOrder:
            theText += theDoc.openDocument(tHandle, False).rstrip("\n")
            theText += "\n\n"

        if self.sourceItem is None:
            self.theParent.makeAlert(
                self.tr("No source document selected. Nothing to do."), nwAlert.ERROR
            )
            return

        srcItem = self.theProject.projTree[self.sourceItem]
        if srcItem is None:
            self.theParent.makeAlert(
                self.tr("Could not parse source document."), nwAlert.ERROR
            )
            return

        nHandle = self.theProject.newFile(srcItem.itemName, srcItem.itemClass, srcItem.itemParent)
        newItem = self.theProject.projTree[nHandle]
        newItem.setStatus(srcItem.itemStatus)

        theDoc.openDocument(nHandle, False)
        theDoc.saveDocument(theText)
        self.theParent.treeView.revealNewTreeItem(nHandle)
        self.theParent.openDocument(nHandle, doScroll=True)

        self._doClose()

        return

    def _doClose(self):
        """Close the dialog window without doing anything.
        """
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
        tHandle = self.theParent.treeView.getSelectedHandle()
        self.sourceItem = tHandle
        if tHandle is None:
            return

        nwItem = self.theProject.projTree[tHandle]
        if nwItem is None:
            return
        if nwItem.itemType is not nwItemType.FOLDER:
            self.theParent.makeAlert(
                self.tr("Element selected in the project tree must be a folder."), nwAlert.ERROR
            )
            return

        for sHandle in self.theParent.treeView.getTreeFromHandle(tHandle):
            newItem = QListWidgetItem()
            nwItem  = self.theProject.projTree[sHandle]
            if nwItem.itemType is not nwItemType.FILE:
                continue
            newItem.setText(nwItem.itemName)
            newItem.setData(Qt.UserRole, sHandle)
            self.listBox.addItem(newItem)

        return

# END Class GuiDocMerge

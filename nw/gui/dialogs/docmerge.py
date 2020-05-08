# -*- coding: utf-8 -*-
"""novelWriter GUI Doc Merge

 novelWriter – GUI Doc Merge
=============================
 Tool for merging multiple documents to one

 File History:
 Created: 2020-01-23 [0.4.3]

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
    QDialog, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton,
    QListWidget, QAbstractItemView, QListWidgetItem
)
from nw.constants import nwAlert, nwItemType
from nw.core import NWDoc

logger = logging.getLogger(__name__)

class GuiDocMerge(QDialog):

    def __init__(self, theParent, theProject):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiDocMerge ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
        self.sourceItem = None

        self.outerBox = QHBoxLayout()
        self.innerBox = QVBoxLayout()
        self.setWindowTitle("Merge Documents")
        self.setLayout(self.outerBox)

        self.guiDeco = self.theParent.theTheme.loadDecoration("merge",(64,64))

        self.outerBox.addWidget(self.guiDeco, 0, Qt.AlignTop)
        self.outerBox.addLayout(self.innerBox)

        self.doMergeForm = QGridLayout()
        self.doMergeForm.setContentsMargins(0,0,0,0)

        self.listBox = QListWidget()
        self.listBox.setDragDropMode(QAbstractItemView.InternalMove)

        self.mergeButton = QPushButton("Merge")
        self.mergeButton.clicked.connect(self._doMerge)

        self.closeButton = QPushButton("Close")
        self.closeButton.clicked.connect(self._doClose)

        self.doMergeForm.addWidget(self.listBox,     0, 0, 1, 3)
        self.doMergeForm.addWidget(self.mergeButton, 1, 1)
        self.doMergeForm.addWidget(self.closeButton, 1, 2)

        self.innerBox.addLayout(self.doMergeForm)

        self.rejected.connect(self._doClose)
        self.show()

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

        theDoc = NWDoc(self.theProject, self.theParent)
        theText = ""
        for tHandle in finalOrder:
            theText += theDoc.openDocument(tHandle, False).rstrip()
            theText += "\n\n"

        if self.sourceItem is None:
            self.theParent.makeAlert((
                "Cannot parse source item."
            ), nwAlert.ERROR)
            return

        srcItem = self.theProject.projTree[self.sourceItem]
        nHandle = self.theProject.newFile(srcItem.itemName, srcItem.itemClass, srcItem.parHandle)
        self.theParent.treeView.revealTreeItem(nHandle)
        theDoc.openDocument(nHandle, False)
        theDoc.saveDocument(theText)
        self.theParent.openDocument(nHandle)

        self.close()

        return

    def _doClose(self):
        """Close the dialog window without doing anything.
        """
        logger.verbose("GuiDocMerge close button clicked")
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
            self.theParent.makeAlert((
                "Element selected in the project tree must be a folder."
            ), nwAlert.ERROR)
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

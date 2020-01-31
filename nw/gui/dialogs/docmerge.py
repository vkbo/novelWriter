# -*- coding: utf-8 -*-
"""novelWriter GUI Doc Merge

 novelWriter – GUI Doc Merge
=============================
 Tool for merging multiple documents to one

 File History:
 Created: 2020-01-23 [0.4.3]

"""

import logging
import nw

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, QLabel,
    QProgressBar, QListWidget, QAbstractItemView, QListWidgetItem
)
from nw.constants import nwFiles, nwAlert, nwItemClass, nwItemType
from nw.project import NWDoc
from nw.tools import OptLastState

logger = logging.getLogger(__name__)

class GuiDocMerge(QDialog):

    def __init__(self, theParent, theProject):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiDocMerge ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
        self.sourceItem = None
        self.optState   = DocMergeLastState(self.theProject,nwFiles.MERGE_OPT)
        self.optState.loadSettings()

        self.outerBox = QHBoxLayout()
        self.innerBox = QVBoxLayout()
        self.setWindowTitle("Merge Documents")
        self.setLayout(self.outerBox)

        self.guiDeco = self.theParent.theTheme.loadDecoration("merge",(64,64))

        self.outerBox.addWidget(self.guiDeco, 0, Qt.AlignTop)
        self.outerBox.addLayout(self.innerBox)

        self.doMergeForm = QGridLayout()
        self.doMergeForm.setContentsMargins(10,5,0,10)

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

        srcItem = self.theProject.getItem(self.sourceItem)
        nHandle = self.theProject.newFile(srcItem.itemName, srcItem.itemClass, srcItem.parHandle)
        self.theParent.treeView.revealTreeItem(nHandle)
        theDoc.openDocument(nHandle, False)
        theDoc.saveDocument(theText)
        self.theParent.openDocument(nHandle)

        self.close()

        return

    def _doClose(self):

        logger.verbose("GuiDocMerge close button clicked")

        self.optState.saveSettings()
        self.close()

        return

    ##
    #  Internal Functions
    ##

    def _populateList(self):

        tHandle = self.theParent.treeView.getSelectedHandle()
        self.sourceItem = tHandle
        if tHandle is None:
            return

        nwItem = self.theProject.getItem(tHandle)
        if nwItem is None:
            return
        if nwItem.itemType is not nwItemType.FOLDER:
            self.theParent.makeAlert((
                "Element selected in the project tree must be a folder."
            ), nwAlert.ERROR)
            return

        for sHandle in self.theParent.treeView.getTreeFromHandle(tHandle):
            newItem = QListWidgetItem()
            nwItem  = self.theProject.getItem(sHandle)
            if nwItem.itemType is not nwItemType.FILE:
                continue
            newItem.setText(nwItem.itemName)
            newItem.setData(Qt.UserRole, sHandle)
            self.listBox.addItem(newItem)

        return

# END Class GuiDocMerge

class DocMergeLastState(OptLastState):

    def __init__(self, theProject, theFile):
        OptLastState.__init__(self, theProject, theFile)
        self.theState   = {
        }
        self.stringOpt = ()
        self.boolOpt   = ()
        self.intOpt    = ()
        return

# END Class DocMergeLastState

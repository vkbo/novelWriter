# -*- coding: utf-8 -*-
"""novelWriter GUI Open Project

 novelWriter – GUI Open Project
================================
 New and open project dialog

 File History:
 Created: 2020-02-26 [0.4.5]

"""

import logging
import nw

from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, QTreeWidget,
    QAbstractItemView, QTreeWidgetItem
)

from nw.common import formatInt

logger = logging.getLogger(__name__)

class GuiProjectLoad(QDialog):

    def __init__(self, theParent):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiProjectLoad ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.sourceItem = None
        self.openPath   = None

        self.outerBox = QHBoxLayout()
        self.innerBox = QVBoxLayout()
        self.setWindowTitle("Open Project")
        self.setLayout(self.outerBox)

        self.guiDeco = self.theParent.theTheme.loadDecoration("nwicon", (128, 128))

        self.outerBox.addWidget(self.guiDeco, 0, Qt.AlignTop)
        self.outerBox.addLayout(self.innerBox)

        self.projectForm = QGridLayout()
        self.projectForm.setContentsMargins(0, 0, 0, 0)

        self.listBox = QTreeWidget()
        self.listBox.setSelectionMode(QAbstractItemView.SingleSelection)
        self.listBox.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.listBox.setColumnCount(4)
        self.listBox.setHeaderLabels(["Working Title","Words","Accessed","Path"])
        self.listBox.setRootIsDecorated(False)

        treeHead = self.listBox.headerItem()
        treeHead.setTextAlignment(1, Qt.AlignRight)

        self.recentButton = QPushButton("Open")
        self.recentButton.clicked.connect(self._doOpenRecent)
        self.browseButton = QPushButton("Browse")
        self.browseButton.clicked.connect(self._doBrowse)
        self.closeButton = QPushButton("Close")
        self.closeButton.clicked.connect(self._doClose)

        self.projectForm.addWidget(self.listBox,      0, 0, 1, 4)
        self.projectForm.addWidget(self.recentButton, 1, 1)
        self.projectForm.addWidget(self.browseButton, 1, 2)
        self.projectForm.addWidget(self.closeButton,  1, 3)
        self.projectForm.setColumnStretch(0, 1)

        self.innerBox.addLayout(self.projectForm)

        self.rejected.connect(self._doClose)
        self.setModal(True)
        self.setMinimumWidth(750)
        self.setMinimumHeight(450)
        self.show()

        self._populateList()

        logger.debug("GuiProjectLoad initialisation complete")

        return

    ##
    #  Buttons
    ##

    def _doOpenRecent(self):
        """Close the dialog window with a recent project selected.
        """
        logger.verbose("GuiProjectLoad open button clicked")

        selItems = self.listBox.selectedItems()
        if selItems:
            self.openPath = selItems[0].text(3)
            self.accept()
        else:
            self.openPath = None

        return

    def _doBrowse(self):
        """Close the dialog window with no selected path, triggering the
        project browser dialog.
        """
        logger.verbose("GuiProjectLoad browse button clicked")
        self.openPath = None
        self.accept()
        return

    def _doClose(self):
        """Close the dialog window without doing anything.
        """
        logger.verbose("GuiProjectLoad close button clicked")
        self.close()
        return

    ##
    #  Internal Functions
    ##

    def _populateList(self):
        """Populate the list box with recent project data.
        """

        listOrder = []
        listData  = {}
        for projPath in self.mainConf.recentProj.keys():
            theEntry = self.mainConf.recentProj[projPath]
            theTitle = ""
            theTime  = 0
            theWords = 0
            if "title" in theEntry.keys():
                theTitle = theEntry["title"]
            if "time" in theEntry.keys():
                theTime = theEntry["time"]
            if "words" in theEntry.keys():
                theWords = theEntry["words"]
            if theTime > 0:
                listOrder.append(theTime)
                listData[theTime] = [theTitle, theWords, projPath]

        self.listBox.clear()
        hasSelection = False
        for timeStamp in sorted(listOrder, reverse=True):
            newItem = QTreeWidgetItem([""]*4)
            newItem.setText(0, listData[timeStamp][0])
            newItem.setText(1, formatInt(listData[timeStamp][1]))
            newItem.setText(2, datetime.fromtimestamp(timeStamp).strftime("%x %X"))
            newItem.setText(3, listData[timeStamp][2])
            newItem.setTextAlignment(1, Qt.AlignRight)
            self.listBox.addTopLevelItem(newItem)
            if not hasSelection:
                newItem.setSelected(True)
                hasSelection = True

        self.listBox.resizeColumnToContents(0)
        self.listBox.resizeColumnToContents(1)
        self.listBox.resizeColumnToContents(2)

        return

# END Class GuiProjectLoad

# -*- coding: utf-8 -*-
"""novelWriter GUI Open Project

 novelWriter – GUI Open Project
================================
 New and open project dialog

 File History:
 Created: 2020-02-26 [0.4.5]

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

from os import path
from datetime import datetime

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, QTreeWidget,
    QAbstractItemView, QTreeWidgetItem, QDialogButtonBox, QLabel, QShortcut,
    QFileDialog, QLineEdit
)

from nw.common import formatInt
from nw.constants import nwFiles

logger = logging.getLogger(__name__)

class GuiProjectLoad(QDialog):

    NONE_STATE = 0
    NEW_STATE  = 1
    OPEN_STATE = 2

    def __init__(self, theParent):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiProjectLoad ...")

        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.theTheme  = theParent.theTheme
        self.openState = self.NONE_STATE
        self.openPath  = None

        self.outerBox = QVBoxLayout()
        self.innerBox = QHBoxLayout()
        self.outerBox.setSpacing(16)
        self.innerBox.setSpacing(16)

        self.setWindowTitle("Open Project")
        self.setMinimumWidth(650)
        self.setMinimumHeight(400)
        self.setModal(True)

        self.guiDeco = self.theTheme.loadDecoration("nwicon", (96, 96))
        self.innerBox.addWidget(self.guiDeco, 0, Qt.AlignTop)

        self.projectForm = QGridLayout()
        self.projectForm.setContentsMargins(0, 0, 0, 0)

        iPx = self.theTheme.textIconSize
        self.listBox = QTreeWidget()
        self.listBox.setSelectionMode(QAbstractItemView.SingleSelection)
        self.listBox.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.listBox.setColumnCount(4)
        self.listBox.setHeaderLabels(["Working Title","Words","Last Opened","Path"])
        self.listBox.setRootIsDecorated(False)
        self.listBox.setColumnHidden(3, True)
        self.listBox.itemSelectionChanged.connect(self._doSelectRecent)
        self.listBox.itemDoubleClicked.connect(self._doOpenRecent)
        self.listBox.setIconSize(QSize(iPx, iPx))

        treeHead = self.listBox.headerItem()
        treeHead.setTextAlignment(1, Qt.AlignRight)
        treeHead.setTextAlignment(2, Qt.AlignRight)
        treeHead.setFont(0, self.theTheme.guiFont)
        treeHead.setFont(1, self.theTheme.guiFont)
        treeHead.setFont(2, self.theTheme.guiFont)

        self.lblRecent = QLabel("<b>Recently Opened Projects</b>")
        self.lblPath   = QLabel("<b>Path</b>")
        self.selPath   = QLineEdit("")
        self.selPath.setReadOnly(True)

        self.browseButton = QPushButton("...")
        self.browseButton.setMaximumWidth(int(2.5*self.theTheme.getTextWidth("...")))
        self.browseButton.clicked.connect(self._doBrowse)

        self.projectForm.addWidget(self.lblRecent,    0, 0, 1, 3)
        self.projectForm.addWidget(self.listBox,      1, 0, 1, 3)
        self.projectForm.addWidget(self.lblPath,      2, 0, 1, 1)
        self.projectForm.addWidget(self.selPath,      2, 1, 1, 1)
        self.projectForm.addWidget(self.browseButton, 2, 2, 1, 1)
        self.projectForm.setColumnStretch(0, 0)
        self.projectForm.setColumnStretch(1, 1)
        self.projectForm.setColumnStretch(2, 0)
        self.projectForm.setVerticalSpacing(4)
        self.projectForm.setHorizontalSpacing(8)

        self.innerBox.addLayout(self.projectForm)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Open | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self._doOpenRecent)
        self.buttonBox.rejected.connect(self._doClose)

        self.newButton = self.buttonBox.addButton("New", QDialogButtonBox.ActionRole)
        self.newButton.clicked.connect(self._doNewProject)

        self.outerBox.addLayout(self.innerBox)
        self.outerBox.addWidget(self.buttonBox)
        self.setLayout(self.outerBox)

        self._populateList()
        self._doSelectRecent()

        keyDelete = QShortcut(self.listBox)
        keyDelete.setKey(QKeySequence(Qt.Key_Delete))
        keyDelete.activated.connect(self._keyPressDelete)

        logger.debug("GuiProjectLoad initialisation complete")

        return

    ##
    #  Buttons
    ##

    def _doOpenRecent(self):
        """Close the dialog window with a recent project selected.
        """
        logger.verbose("GuiProjectLoad open button clicked")
        self._saveDialogState()
        selItems = self.listBox.selectedItems()
        if selItems:
            self.openPath = selItems[0].text(3)
            self.openState = self.OPEN_STATE
            self.accept()
        else:
            self.openPath = None
            self.openState = self.NONE_STATE
        return

    def _doSelectRecent(self):
        """A recent item has been selected.
        """
        selList = self.listBox.selectedItems()
        if selList:
            self.selPath.setText(selList[0].text(3))
        return

    def _doBrowse(self):
        """Close the dialog window with no selected path, triggering the
        project browser dialog.
        """
        logger.verbose("GuiProjectLoad browse button clicked")
        if self.mainConf.showGUI:
            dlgOpt  = QFileDialog.Options()
            dlgOpt |= QFileDialog.DontUseNativeDialog
            projFile, _ = QFileDialog.getOpenFileName(
                self, "Open novelWriter Project", "",
                "novelWriter Project File (%s);;All Files (*)" % nwFiles.PROJ_FILE,
                options=dlgOpt
            )
            if projFile:
                thePath = path.abspath(path.dirname(projFile))
                self.selPath.setText(thePath)
                self.openPath = thePath
                self.openState = self.OPEN_STATE
                self.accept()
        return

    def _doClose(self):
        """Close the dialog window without doing anything.
        """
        logger.verbose("GuiProjectLoad close button clicked")
        self._saveDialogState()
        self.close()
        return

    def _doNewProject(self):
        """Create a new project.
        """
        logger.verbose("GuiProjectLoad new project button clicked")
        self._saveDialogState()
        self.openPath = None
        self.openState = self.NEW_STATE
        self.accept()
        return

    def _keyPressDelete(self):
        """Remove an entry from the recent projects list.
        """
        selList = self.listBox.selectedItems()
        if selList:
            self.mainConf.removeFromRecentCache(selList[0].text(3))
            self._populateList()
        return

    ##
    #  Internal Functions
    ##

    def _saveDialogState(self):
        """Save the changes made to the dialog.
        """
        colWidths = [50]*3
        for i in range(3):
            colWidths[i] = self.listBox.columnWidth(i)
        self.mainConf.setProjColWidths(colWidths)
        return

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
            newItem.setIcon(0, self.theParent.theTheme.getIcon("proj_nwx"))
            newItem.setText(0, listData[timeStamp][0])
            newItem.setText(1, formatInt(listData[timeStamp][1]))
            newItem.setText(2, datetime.fromtimestamp(timeStamp).strftime("%x %X"))
            newItem.setText(3, listData[timeStamp][2])
            newItem.setTextAlignment(0, Qt.AlignLeft  | Qt.AlignVCenter)
            newItem.setTextAlignment(1, Qt.AlignRight | Qt.AlignVCenter)
            newItem.setTextAlignment(2, Qt.AlignRight | Qt.AlignVCenter)
            newItem.setFont(0, self.theTheme.guiFont)
            newItem.setFont(1, self.theTheme.guiFont)
            newItem.setFont(2, self.theTheme.guiFont)
            self.listBox.addTopLevelItem(newItem)
            if not hasSelection:
                newItem.setSelected(True)
                hasSelection = True

        for i in range(3):
            self.listBox.setColumnWidth(i, self.mainConf.projColWidth[i])

        return

# END Class GuiProjectLoad

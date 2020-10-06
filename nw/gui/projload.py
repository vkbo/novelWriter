# -*- coding: utf-8 -*-
"""novelWriter GUI Open Project

 novelWriter – GUI Open Project
================================
 New and open project dialog

 File History:
 Created: 2020-02-26 [0.4.5]

 This file is a part of novelWriter
 Copyright 2018–2020, Veronica Berglyd Olsen

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
import os

from datetime import datetime

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, QTreeWidget,
    QAbstractItemView, QTreeWidgetItem, QDialogButtonBox, QLabel, QShortcut,
    QFileDialog, QLineEdit, QMessageBox
)

from nw.common import formatInt
from nw.constants import nwFiles

logger = logging.getLogger(__name__)

class GuiProjectLoad(QDialog):

    NONE_STATE = 0
    NEW_STATE  = 1
    OPEN_STATE = 2

    C_NAME  = 0
    C_COUNT = 1
    C_TIME  = 2

    def __init__(self, theParent):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising GuiProjectLoad ...")
        self.setObjectName("GuiProjectLoad")

        self.mainConf  = nw.CONFIG
        self.theParent = theParent
        self.theTheme  = theParent.theTheme
        self.openState = self.NONE_STATE
        self.openPath  = None

        sPx = self.mainConf.pxInt(16)
        nPx = self.mainConf.pxInt(96)
        iPx = self.theTheme.baseIconSize

        self.outerBox = QVBoxLayout()
        self.innerBox = QHBoxLayout()
        self.outerBox.setSpacing(sPx)
        self.innerBox.setSpacing(sPx)

        self.setWindowTitle("Open Project")
        self.setMinimumWidth(self.mainConf.pxInt(650))
        self.setMinimumHeight(self.mainConf.pxInt(400))
        self.setModal(True)

        self.nwIcon = QLabel()
        self.nwIcon.setPixmap(self.theParent.theTheme.getPixmap("novelwriter", (nPx, nPx)))
        self.innerBox.addWidget(self.nwIcon, 0, Qt.AlignTop)

        self.projectForm = QGridLayout()
        self.projectForm.setContentsMargins(0, 0, 0, 0)

        self.listBox = QTreeWidget()
        self.listBox.setSelectionMode(QAbstractItemView.SingleSelection)
        self.listBox.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.listBox.setColumnCount(3)
        self.listBox.setHeaderLabels(["Working Title", "Words", "Last Opened"])
        self.listBox.setRootIsDecorated(False)
        self.listBox.itemSelectionChanged.connect(self._doSelectRecent)
        self.listBox.itemDoubleClicked.connect(self._doOpenRecent)
        self.listBox.setIconSize(QSize(iPx, iPx))

        treeHead = self.listBox.headerItem()
        treeHead.setTextAlignment(self.C_COUNT, Qt.AlignRight)
        treeHead.setTextAlignment(self.C_TIME, Qt.AlignRight)

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
        self.projectForm.setVerticalSpacing(self.mainConf.pxInt(4))
        self.projectForm.setHorizontalSpacing(self.mainConf.pxInt(8))

        self.innerBox.addLayout(self.projectForm)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Open | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self._doOpenRecent)
        self.buttonBox.rejected.connect(self._doCancel)

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
        self._saveSettings()

        selItems = self.listBox.selectedItems()
        if selItems:
            self.openPath = selItems[0].data(self.C_NAME, Qt.UserRole)
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
            self.selPath.setText(selList[0].data(self.C_NAME, Qt.UserRole))
        return

    def _doBrowse(self):
        """Browse for a folder path.
        """
        logger.verbose("GuiProjectLoad browse button clicked")
        dlgOpt  = QFileDialog.Options()
        dlgOpt |= QFileDialog.DontUseNativeDialog
        projFile, _ = QFileDialog.getOpenFileName(
            self, "Open novelWriter Project", "",
            "novelWriter Project File (%s);;All Files (*)" % nwFiles.PROJ_FILE,
            options=dlgOpt
        )
        if projFile:
            thePath = os.path.abspath(os.path.dirname(projFile))
            self.selPath.setText(thePath)
            self.openPath = thePath
            self.openState = self.OPEN_STATE
            self.accept()

        return

    def _doCancel(self):
        """Close the dialog window without doing anything.
        """
        logger.verbose("GuiProjectLoad close button clicked")
        self.openPath = None
        self.openState = self.NONE_STATE
        self.close()
        return

    def _doNewProject(self):
        """Create a new project.
        """
        logger.verbose("GuiProjectLoad new project button clicked")
        self._saveSettings()
        self.openPath = None
        self.openState = self.NEW_STATE
        self.accept()
        return

    def _keyPressDelete(self):
        """Remove an entry from the recent projects list.
        """
        selList = self.listBox.selectedItems()
        if selList:
            msgBox = QMessageBox()
            msgRes = msgBox.question(
                self, "Remove Entry",
                "Remove the selected entry from the recent projects list?"
            )
            if msgRes == QMessageBox.Yes:
                self.mainConf.removeFromRecentCache(
                    selList[0].data(self.C_NAME, Qt.UserRole)
                )
                self._populateList()

        return

    ##
    #  Events
    ##

    def closeEvent(self, theEvent):
        """Capture the user closing the dialog so we can save settings.
        """
        self._saveSettings()
        theEvent.accept()
        return

    ##
    #  Internal Functions
    ##

    def _saveSettings(self):
        """Save the changes made to the dialog.
        """
        colWidths = [0, 0, 0]
        colWidths[self.C_NAME]  = self.listBox.columnWidth(self.C_NAME)
        colWidths[self.C_COUNT] = self.listBox.columnWidth(self.C_COUNT)
        colWidths[self.C_TIME]  = self.listBox.columnWidth(self.C_TIME)
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
            newItem.setIcon(self.C_NAME,  self.theParent.theTheme.getIcon("proj_nwx"))
            newItem.setText(self.C_NAME,  listData[timeStamp][0])
            newItem.setData(self.C_NAME,  Qt.UserRole, listData[timeStamp][2])
            newItem.setText(self.C_COUNT, formatInt(listData[timeStamp][1]))
            newItem.setText(self.C_TIME,  datetime.fromtimestamp(timeStamp).strftime("%x %X"))
            newItem.setTextAlignment(self.C_NAME,  Qt.AlignLeft  | Qt.AlignVCenter)
            newItem.setTextAlignment(self.C_COUNT, Qt.AlignRight | Qt.AlignVCenter)
            newItem.setTextAlignment(self.C_TIME,  Qt.AlignRight | Qt.AlignVCenter)
            newItem.setFont(self.C_TIME, self.theTheme.guiFontFixed)
            self.listBox.addTopLevelItem(newItem)
            if not hasSelection:
                newItem.setSelected(True)
                hasSelection = True

        projColWidth = self.mainConf.getProjColWidths()
        if len(projColWidth) == 3:
            self.listBox.setColumnWidth(self.C_NAME,  projColWidth[self.C_NAME])
            self.listBox.setColumnWidth(self.C_COUNT, projColWidth[self.C_COUNT])
            self.listBox.setColumnWidth(self.C_TIME,  projColWidth[self.C_TIME])

        return

# END Class GuiProjectLoad

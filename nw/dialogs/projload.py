# -*- coding: utf-8 -*-
"""
novelWriter – GUI Open Project
==============================
GUI class for the load/browse/new project dialog

File History:
Created: 2020-02-26 [0.4.5]

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
import os

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

        self.setWindowTitle(self.tr("Open Project"))
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
        self.listBox.setHeaderLabels([
            self.tr("Working Title"),
            self.tr("Words"),
            self.tr("Last Opened"),
        ])
        self.listBox.setRootIsDecorated(False)
        self.listBox.itemSelectionChanged.connect(self._doSelectRecent)
        self.listBox.itemDoubleClicked.connect(self._doOpenRecent)
        self.listBox.setIconSize(QSize(iPx, iPx))

        treeHead = self.listBox.headerItem()
        treeHead.setTextAlignment(self.C_COUNT, Qt.AlignRight)
        treeHead.setTextAlignment(self.C_TIME, Qt.AlignRight)

        self.lblRecent = QLabel("<b>%s</b>" % self.tr("Recently Opened Projects"))
        self.lblPath   = QLabel("<b>%s</b>" % self.tr("Path"))
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

        self.newButton = self.buttonBox.addButton(self.tr("New"), QDialogButtonBox.ActionRole)
        self.newButton.clicked.connect(self._doNewProject)

        self.delButton = self.buttonBox.addButton(self.tr("Remove"), QDialogButtonBox.ActionRole)
        self.delButton.clicked.connect(self._doDeleteRecent)

        self.outerBox.addLayout(self.innerBox)
        self.outerBox.addWidget(self.buttonBox)
        self.setLayout(self.outerBox)

        self._populateList()
        self._doSelectRecent()

        keyDelete = QShortcut(self.listBox)
        keyDelete.setKey(QKeySequence(Qt.Key_Delete))
        keyDelete.activated.connect(self._doDeleteRecent)

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

        self.openPath = None
        self.openState = self.NONE_STATE

        selItems = self.listBox.selectedItems()
        if selItems:
            self.openPath = selItems[0].data(self.C_NAME, Qt.UserRole)
            self.openState = self.OPEN_STATE
            self.accept()

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
        extFilter = [
            self.tr("novelWriter Project File ({0})").format(nwFiles.PROJ_FILE),
            self.tr("All files ({0})").format("*"),
        ]
        projFile, _ = QFileDialog.getOpenFileName(
            self, self.tr("Open Project"), "", filter=";;".join(extFilter)
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

    def _doDeleteRecent(self):
        """Remove an entry from the recent projects list.
        """
        selList = self.listBox.selectedItems()
        if selList:
            projName = selList[0].text(self.C_NAME)
            msgYes = self.theParent.askQuestion(
                self.tr("Remove Entry"),
                self.tr(
                    "Remove '{0}' from the recent projects list? "
                    "The project files will not be deleted."
                ).format(projName)
            )
            if msgYes:
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
        dataList = []
        for projPath in self.mainConf.recentProj:
            theEntry = self.mainConf.recentProj[projPath]
            theTitle = theEntry.get("title", "")
            theTime  = theEntry.get("time", 0)
            theWords = theEntry.get("words", 0)
            dataList.append([theTitle, theTime, theWords, projPath])

        self.listBox.clear()
        sortList = sorted(dataList, key=lambda x: x[1], reverse=True)
        for theTitle, theTime, theWords, projPath in sortList:
            newItem = QTreeWidgetItem([""]*4)
            newItem.setIcon(self.C_NAME,  self.theParent.theTheme.getIcon("proj_nwx"))
            newItem.setText(self.C_NAME,  theTitle)
            newItem.setData(self.C_NAME,  Qt.UserRole, projPath)
            newItem.setText(self.C_COUNT, formatInt(theWords))
            newItem.setText(self.C_TIME,  datetime.fromtimestamp(theTime).strftime("%x %X"))
            newItem.setTextAlignment(self.C_NAME,  Qt.AlignLeft  | Qt.AlignVCenter)
            newItem.setTextAlignment(self.C_COUNT, Qt.AlignRight | Qt.AlignVCenter)
            newItem.setTextAlignment(self.C_TIME,  Qt.AlignRight | Qt.AlignVCenter)
            newItem.setFont(self.C_TIME, self.theTheme.guiFontFixed)
            self.listBox.addTopLevelItem(newItem)

        if self.listBox.topLevelItemCount() > 0:
            self.listBox.topLevelItem(0).setSelected(True)

        projColWidth = self.mainConf.getProjColWidths()
        if len(projColWidth) == 3:
            self.listBox.setColumnWidth(self.C_NAME,  projColWidth[self.C_NAME])
            self.listBox.setColumnWidth(self.C_COUNT, projColWidth[self.C_COUNT])
            self.listBox.setColumnWidth(self.C_TIME,  projColWidth[self.C_TIME])

        return

# END Class GuiProjectLoad

# -*- coding: utf-8 -*-
"""
novelWriter – GUI Version Tree
==============================
GUI class for the main window tree of document versions

File History:
Created: 2021-05-16 [1.4a0]

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

from time import time
from datetime import datetime

from PyQt5.QtCore import Qt, QSize, pyqtSlot
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QAbstractItemView

from nw.core import NWDoc

logger = logging.getLogger(__name__)

class GuiVersionTree(QTreeWidget):

    C_DATE = 0
    C_NOTE = 1

    def __init__(self, theParent):
        QTreeWidget.__init__(self, theParent)

        logger.debug("Initialising GuiVersionTree ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theTheme   = theParent.theTheme
        self.theProject = theParent.theProject

        # Internal Variables
        self._lastBuild = 0
        self._docHandle = None

        # Build GUI
        iPx = self.theTheme.baseIconSize
        self.setIconSize(QSize(iPx, iPx))
        self.setIndentation(iPx)
        self.setColumnCount(2)
        self.setHeaderLabels([self.tr("Date"), self.tr("Note")])
        self.itemDoubleClicked.connect(self._treeDoubleClick)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setExpandsOnDoubleClick(False)
        self.setDragEnabled(False)

        treeHeader = self.header()
        treeHeader.setStretchLastSection(True)
        treeHeader.setMinimumSectionSize(iPx + 6)

        # Get user's column width preferences for NAME and COUNT
        treeColWidth = self.mainConf.getVersionColWidths()
        if len(treeColWidth) <= 2:
            for colN, colW in enumerate(treeColWidth):
                self.setColumnWidth(colN, colW)

        # The last column should just auto-scale
        self.resizeColumnToContents(self.C_NOTE)

        # Set custom settings
        self.initTree()

        logger.debug("GuiVersionTree initialisation complete")

        # Internal Mapping
        self.makeAlert = self.theParent.makeAlert

        return

    def initTree(self):
        """Set or update tree widget settings.
        """
        # Scroll bars
        if self.mainConf.hideVScroll:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        if self.mainConf.hideHScroll:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        else:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        return

    ##
    #  Class Methods
    ##

    def clearTree(self):
        """Clear the GUI content and the related maps.
        """
        self.clear()
        self._lastBuild = 0
        return

    def getColumnSizes(self):
        """Return the column widths for the tree columns.
        """
        retVals = [self.columnWidth(0)]
        return retVals

    ##
    #  Events
    ##

    def mousePressEvent(self, theEvent):
        """Overload mousePressEvent to clear selection if clicking the
        mouse in a blank area of the tree view, and to load a document
        for viewing if the user middle-clicked.
        """
        QTreeWidget.mousePressEvent(self, theEvent)

        if theEvent.button() == Qt.LeftButton:
            selItem = self.indexAt(theEvent.pos())
            if not selItem.isValid():
                self.clearSelection()

        # elif theEvent.button() == Qt.MiddleButton:
        #     selItem = self.itemAt(theEvent.pos())
        #     if not isinstance(selItem, QTreeWidgetItem):
        #         return

        #     tHandle = self.getSelectedHandle()
        #     if tHandle is None:
        #         return

        #     self.theParent.viewDocument(tHandle)

        return

    ##
    #  Slots
    ##

    @pyqtSlot(str)
    def doUpdateDocument(self, tHandle):
        """The editor's document handle has changed.
        """
        logger.debug("Refreshing version tree with %s" % tHandle)
        self._docHandle = tHandle
        self._populateTree()
        return

    def _treeDoubleClick(self, tItem, tCol):
        return

    ##
    #  Internal Functions
    ##

    def _populateTree(self):
        """Build the tree based on the project index.
        """
        if self._docHandle is None:
            return False

        nwItem = self.theProject.projTree[self._docHandle]
        if nwItem is None:
            return False

        self.clearTree()

        # Session Version
        # ===============

        sessDir = QTreeWidgetItem()
        sessDir.setText(self.C_DATE, self.tr("Session"))
        sessDir.setIcon(self.C_DATE, self.theTheme.getIcon("proj_folder"))
        self.addTopLevelItem(sessDir)

        sessTime = datetime.fromtimestamp(self.theProject.projOpened).strftime("%c")
        sessNote = self.tr("Current Session")
        sessItem = QTreeWidgetItem()
        if nwItem.sessionBak:
            sessItem.setText(self.C_DATE, sessTime)
            sessItem.setText(self.C_NOTE, sessNote)
            sessItem.setToolTip(self.C_DATE, sessTime)
            sessItem.setToolTip(self.C_NOTE, sessNote)
            sessItem.setData(self.C_DATE, Qt.UserRole, "Session")
            sessItem.setIcon(self.C_DATE, self.theTheme.getIcon("proj_document"))
        else:
            sessItem.setText(self.C_DATE, self.tr("None"))
            sessItem.setData(self.C_DATE, Qt.UserRole, "None")
            sessItem.setIcon(self.C_DATE, self.theTheme.getIcon("cross"))

        sessDir.addChild(sessItem)
        sessDir.setExpanded(True)

        # Other Versions
        # ==============

        versDir = QTreeWidgetItem()
        versDir.setText(self.C_DATE, self.tr("Versions"))
        versDir.setIcon(self.C_DATE, self.theTheme.getIcon("proj_folder"))
        self.addTopLevelItem(versDir)

        nwDoc = NWDoc(self.theProject, self._docHandle)
        versList = nwDoc.listVersions()
        if versList:
            for versName, versDate, versNote in versList:
                versTime = datetime.fromtimestamp(versDate).strftime("%c")

                versItem = QTreeWidgetItem()
                versItem.setText(self.C_DATE, versTime)
                versItem.setText(self.C_NOTE, versNote)
                versItem.setToolTip(self.C_DATE, versTime)
                versItem.setToolTip(self.C_NOTE, versNote)
                versItem.setData(self.C_DATE, Qt.UserRole, versName)
                versItem.setIcon(self.C_DATE, self.theTheme.getIcon("proj_document"))

                versDir.addChild(versItem)
        else:
            versItem = QTreeWidgetItem()
            versItem.setText(self.C_DATE, self.tr("None"))
            versItem.setData(self.C_DATE, Qt.UserRole, "None")
            versItem.setIcon(self.C_DATE, self.theTheme.getIcon("cross"))
            versDir.addChild(versItem)

        versDir.setExpanded(True)

        self._lastBuild = time()

        return

# END Class GuiVersionTree

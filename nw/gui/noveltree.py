# -*- coding: utf-8 -*-
"""novelWriter GUI Novel Tree

 novelWriter – GUI Novel Tree
==============================
 Class holding the project's novel files tree view

 File History:
 Created: 2020-12-20 [1.1a0]

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

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QAbstractItemView

from nw.constants import nwKeyWords

logger = logging.getLogger(__name__)

class GuiNovelTree(QTreeWidget):

    C_TITLE = 0
    C_WORDS = 1
    C_POV   = 2

    def __init__(self, theParent):
        QTreeWidget.__init__(self, theParent)

        logger.debug("Initialising GuiNovelTree ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theTheme   = theParent.theTheme
        self.theProject = theParent.theProject
        self.theIndex   = theParent.theIndex

        # Tree State
        self.lastBuild = 0
        self.treeMap = {}

        # Build GUI
        iPx = self.theTheme.baseIconSize
        self.setIconSize(QSize(iPx, iPx))
        self.setIndentation(iPx)
        self.setColumnCount(3)
        self.setHeaderLabels(["Title", "Words", "POV"])
        self.itemDoubleClicked.connect(self._treeDoubleClick)
        self.itemSelectionChanged.connect(self._itemSelected)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setExpandsOnDoubleClick(False)
        self.setDragEnabled(False)

        treeHeadItem = self.headerItem()
        treeHeadItem.setTextAlignment(self.C_WORDS, Qt.AlignRight)
        treeHeadItem.setToolTip(self.C_TITLE, "Section title")
        treeHeadItem.setToolTip(self.C_WORDS, "Word count")
        treeHeadItem.setToolTip(self.C_POV,   "Point-of-view character")

        # Get user's column width preferences for NAME and COUNT
        treeColWidth = self.mainConf.getNovelColWidths()
        if len(treeColWidth) <= 3:
            for colN, colW in enumerate(treeColWidth):
                self.setColumnWidth(colN, colW)

        # The last column should just auto-scale
        self.resizeColumnToContents(self.C_POV)

        # Set custom settings
        self.initTree()

        logger.debug("GuiNovelTree initialisation complete")

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
        self.treeMap = {}
        return

    def refreshTree(self, overRide=False):
        """Called whenever the Novel tab is activated.
        """
        self._populateTree()
        return

    def getColumnSizes(self):
        """Return the column widths for the tree columns.
        """
        retVals = [
            self.columnWidth(0),
            self.columnWidth(1),
        ]
        return retVals

    ##
    #  Slots
    ##

    def _treeDoubleClick(self, tItem, tCol):
        """Extract the handle and line number of the title double-
        clicked, and send it to the main gui class for opening in the
        document editor.
        """
        theData = tItem.data(self.C_TITLE, Qt.UserRole)
        tHandle = theData[0]
        try:
            tLine = int(theData[1])
        except Exception:
            tLine = 1

        logger.verbose("User selected entry with handle %s on line %s" % (tHandle, tLine))
        self.theParent.openDocument(tHandle, tLine=tLine-1, doScroll=True)

        return

    def _itemSelected(self):
        """Extract the handle and line number of the currently selected
        title, and send it to the tree meta panel.
        """
        selItems = self.selectedItems()
        if selItems:
            tHandle = selItems[0].data(self.C_TITLE, Qt.UserRole)[0]
            self.theParent.treeMeta.updateViewBox(tHandle)

        return

    ##
    #  Internal Functions
    ##

    def _populateTree(self):
        """Build the tree based on the project index.
        """
        self.clear()

        for titleKey in self.theIndex.getNovelStructure(skipExcluded=True):

            if len(titleKey) < 16:
                continue

            tHandle = titleKey[:13]
            sTitle  = titleKey[14:]

            if tHandle not in self.theIndex.novelIndex:
                continue
            if sTitle not in self.theIndex.novelIndex[tHandle]:
                continue

            tLevel = self.theIndex.novelIndex[tHandle][sTitle]["level"]
            tItem  = self._createTreeItem(tHandle, sTitle, tLevel)
            self.treeMap[titleKey] = tItem

            if tLevel == "H1":
                currTitle = tItem
                self.addTopLevelItem(tItem)
            elif tLevel == "H2":
                if currTitle is None:
                    self.addTopLevelItem(tItem)
                else:
                    currTitle.addChild(tItem)
                currChapter = tItem
            elif tLevel == "H3":
                if currChapter is None:
                    if currTitle is None:
                        self.addTopLevelItem(tItem)
                    else:
                        currTitle.addChild(tItem)
                else:
                    currChapter.addChild(tItem)
                currScene = tItem
            elif tLevel == "H4":
                if currScene is None:
                    if currChapter is None:
                        if currTitle is None:
                            self.addTopLevelItem(tItem)
                        else:
                            currTitle.addChild(tItem)
                    else:
                        currChapter.addChild(tItem)
                else:
                    currScene.addChild(tItem)

            tItem.setExpanded(True)

        self.lastBuild = time()

        return

    def _createTreeItem(self, tHandle, sTitle, tLevel):
        """Populate a tree item with all the column values.
        """
        novIdx = self.theIndex.novelIndex[tHandle][sTitle]

        newItem = QTreeWidgetItem()
        hIcon   = "doc_%s" % tLevel.lower()
        theData = (tHandle, sTitle[1:].lstrip("0"))

        wC = int(novIdx["wCount"])

        newItem.setText(self.C_TITLE, novIdx["title"])
        newItem.setData(self.C_TITLE, Qt.UserRole, theData)
        newItem.setIcon(self.C_TITLE, self.theTheme.getIcon(hIcon))
        newItem.setText(self.C_WORDS, f"{wC:n}")
        newItem.setTextAlignment(self.C_WORDS, Qt.AlignRight)

        theRefs = self.theIndex.getReferences(tHandle, sTitle)
        newItem.setText(self.C_POV, ", ".join(theRefs[nwKeyWords.POV_KEY]))

        return newItem

# END Class GuiNovelTree

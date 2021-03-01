# -*- coding: utf-8 -*-
"""
novelWriter – GUI Project Outline
=================================
GUI class for the project outline view

File History:
Created: 2019-11-16 [0.4.1]

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

from time import time

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QMenu, QAction, QAbstractItemView
)

from nw.constants import nwKeyWords, nwLabels, nwOutline

logger = logging.getLogger(__name__)

class GuiOutline(QTreeWidget):

    DEF_WIDTH = {
        nwOutline.TITLE  : 200,
        nwOutline.LEVEL  : 40,
        nwOutline.LABEL  : 150,
        nwOutline.LINE   : 40,
        nwOutline.CCOUNT : 50,
        nwOutline.WCOUNT : 50,
        nwOutline.PCOUNT : 50,
        nwOutline.POV    : 100,
        nwOutline.CHAR   : 100,
        nwOutline.PLOT   : 100,
        nwOutline.TIME   : 100,
        nwOutline.WORLD  : 100,
        nwOutline.OBJECT : 100,
        nwOutline.ENTITY : 100,
        nwOutline.CUSTOM : 100,
        nwOutline.SYNOP  : 200,
    }

    DEF_HIDDEN = {
        nwOutline.TITLE  : False,
        nwOutline.LEVEL  : True,
        nwOutline.LABEL  : False,
        nwOutline.LINE   : True,
        nwOutline.CCOUNT : True,
        nwOutline.WCOUNT : False,
        nwOutline.PCOUNT : False,
        nwOutline.POV    : False,
        nwOutline.CHAR   : False,
        nwOutline.PLOT   : False,
        nwOutline.TIME   : True,
        nwOutline.WORLD  : False,
        nwOutline.OBJECT : True,
        nwOutline.ENTITY : True,
        nwOutline.CUSTOM : True,
        nwOutline.SYNOP  : False,
    }

    def __init__(self, theParent):
        QTreeWidget.__init__(self, theParent)

        logger.debug("Initialising GuiOutline ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theParent.theProject
        self.theTheme   = theParent.theTheme
        self.theIndex   = theParent.theIndex
        self.optState   = theParent.theProject.optState
        self.headerMenu = GuiOutlineHeaderMenu(self)

        self.firstView = True
        self.lastBuild = 0

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setExpandsOnDoubleClick(False)
        self.setDragEnabled(False)
        self.itemDoubleClicked.connect(self._treeDoubleClick)
        self.itemSelectionChanged.connect(self._itemSelected)

        iPx = self.theTheme.baseIconSize
        self.setIconSize(QSize(iPx, iPx))
        self.setIndentation(iPx)

        self.treeHead = self.header()
        self.treeHead.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeHead.customContextMenuRequested.connect(self._headerRightClick)
        self.treeHead.sectionMoved.connect(self._columnMoved)

        self.treeMap   = {}
        self.treeOrder = []
        self.colWidth  = {}
        self.colHidden = {}
        self.colIndex  = {}
        self.treeNCols = 0

        self.initOutline()
        self.clearOutline()
        self.headerMenu.setHiddenState(self.colHidden)

        logger.debug("GuiOutline initialisation complete")

        return

    def initOutline(self):
        """Set or update outline settings.
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

    def clearOutline(self):
        """Clear the tree and header and set the default values for the
        columns arrays.
        """
        self.clear()
        self.setColumnCount(1)
        self.setHeaderLabel(nwLabels.OUTLINE_COLS[nwOutline.TITLE])

        self.treeOrder = []
        self.colWidth  = {}
        self.colHidden = {}
        self.colIndex  = {}
        self.treeNCols = 0

        for i, hItem in enumerate(nwOutline):
            self.treeOrder.append(hItem)
            self.colWidth[hItem] = self.DEF_WIDTH[hItem]
            self.colHidden[hItem] = self.DEF_HIDDEN[hItem]

        self.treeNCols = len(self.treeOrder)

        return

    def refreshTree(self, overRide=False, novelChanged=False):
        """Called whenever the Outline tab is activated and controls
        what data to load, and if necessary, force a rebuild of the
        tree.
        """
        # If it's the first time, we always build
        if self.firstView or self.firstView and overRide:
            self._loadHeaderState()
            self._populateTree()
            self.firstView = False
            return

        # If the novel index or novel tree has changed since the tree
        # was last built, we rebuild the tree from the updated index.
        indexChanged = self.theIndex.novelChangedSince(self.lastBuild)
        doBuild = (novelChanged or indexChanged) and self.theProject.autoOutline
        if doBuild or overRide:
            logger.debug("Rebuilding Project Outline")
            self._populateTree()

        return

    def closeOutline(self):
        """Called before a project is closed.
        """
        self._saveHeaderState()
        self.clearOutline()
        self.firstView = True
        return

    ##
    #  Slots
    ##

    def _treeDoubleClick(self, tItem, tCol):
        """Extract the handle and line number of the title double-
        clicked, and send it to the main gui class for opening in the
        document editor.
        """
        tHandle = tItem.data(self.colIndex[nwOutline.TITLE], Qt.UserRole)
        try:
            tLine = int(tItem.text(self.colIndex[nwOutline.LINE]))
        except Exception:
            tLine = 1

        logger.verbose("User selected entry with handle %s on line %s" % (tHandle, tLine))
        self.theParent.openDocument(tHandle, tLine=tLine-1, doScroll=True)

        return

    def _itemSelected(self):
        """Extract the handle and line number of the currently selected
        title, and send it to the details panel.
        """
        selItems = self.selectedItems()
        if selItems:
            tHandle = selItems[0].data(self.colIndex[nwOutline.TITLE], Qt.UserRole)
            sTitle  = selItems[0].data(self.colIndex[nwOutline.LINE], Qt.UserRole)
            self.theParent.projMeta.showItem(tHandle, sTitle)
            self.theParent.treeView.setSelectedHandle(tHandle)

        return

    def _headerRightClick(self, clickPos):
        """Show the header column menu.
        """
        self.headerMenu.exec_(self.mapToGlobal(clickPos))
        return

    def _columnMoved(self, logIdx, oldVisualIdx, newVisualIdx):
        """Make sure the order array is up to date with the actual order
        of the columns.
        """
        self.treeOrder.insert(newVisualIdx, self.treeOrder.pop(oldVisualIdx))
        self._saveHeaderState()
        return

    def _menuColumnToggled(self, isChecked, theItem):
        """Receive the changes to column visibility forwarded by the
        header context menu.
        """
        logger.verbose("User toggled Outline column '%s'" % theItem.name)
        if theItem in self.colIndex:
            self.setColumnHidden(self.colIndex[theItem], not isChecked)
            self._saveHeaderState()

        return

    ##
    #  Internal Functions
    ##

    def _loadHeaderState(self):
        """Load the state of the main tree header, that is, column order
        and column width.
        """
        # Load whatever we saved last time, regardless of wether it
        # contains the correct names or number of columns. The names
        # must be valid though.
        tempOrder = self.optState.getValue("GuiOutline", "headerOrder", [])
        treeOrder = []
        for hName in tempOrder:
            try:
                treeOrder.append(nwOutline[hName])
            except Exception:
                logger.warning("Ignored unknown outline column '%s'" % str(hName))

        # Add columns that was not in the file to the treeOrder array.
        for hItem in nwOutline:
            if hItem not in treeOrder:
                treeOrder.append(hItem)

        # Check that we now have a complete list, and only if so, save
        # the order loaded from file. Otherwise, we keep the default.
        if len(treeOrder) == self.treeNCols:
            self.treeOrder = treeOrder
        else:
            logger.error("Failed to extract outline column order from previous session")
            logger.error("Column count doesn't match %d != %d" % (len(treeOrder), self.treeNCols))

        # We load whatever column widths and hidden states we find in
        # the file, and leave the rest in their default state.
        tmpWidth = self.optState.getValue("GuiOutline", "columnWidth", {})
        for hName in tmpWidth:
            try:
                self.colWidth[nwOutline[hName]] = self.mainConf.pxInt(tmpWidth[hName])
            except Exception:
                logger.warning("Ignored unknown outline column '%s'" % str(hName))

        tmpHidden = self.optState.getValue("GuiOutline", "columnHidden", {})
        for hName in tmpHidden:
            try:
                self.colHidden[nwOutline[hName]] = tmpHidden[hName]
            except Exception:
                logger.warning("Ignored unknown outline column '%s'" % str(hName))

        self.headerMenu.setHiddenState(self.colHidden)

        return

    def _saveHeaderState(self):
        """Save the state of the main tree header, that is, column
        order, column width and column hidden state. We don't want to
        save the current width of hidden columns though. This preserves
        the last known width in case they're unhidden again.
        """
        # If we haven't built the tree, there is nothing to save.
        if self.lastBuild == 0:
            return

        treeOrder = []
        colWidth  = {}
        colHidden = {}

        for hItem in nwOutline:
            colWidth[hItem.name] = self.mainConf.rpxInt(self.colWidth[hItem])
            colHidden[hItem.name] = self.colHidden[hItem]

        for iCol in range(self.columnCount()):
            hName = self.treeOrder[iCol].name
            treeOrder.append(hName)

            iLog = self.treeHead.logicalIndex(iCol)
            logWidth = self.mainConf.rpxInt(self.columnWidth(iLog))
            logHidden = self.isColumnHidden(iLog)

            colHidden[hName] = logHidden
            if not logHidden and logWidth > 0:
                colWidth[hName] = logWidth

        self.optState.setValue("GuiOutline", "headerOrder",  treeOrder)
        self.optState.setValue("GuiOutline", "columnWidth",  colWidth)
        self.optState.setValue("GuiOutline", "columnHidden", colHidden)
        self.optState.saveSettings()

        return

    def _populateTree(self):
        """Build the tree based on the project index, and the header
        based on the defined constants, default values and user selected
        width, order and hidden state. All columns are populated, even
        if they are hidden. This ensures that showing and hiding columns
        is fast and doesn't require a rebuild of the tree.
        """
        self.clear()

        if self.firstView:
            theLabels = []
            for i, hItem in enumerate(self.treeOrder):
                theLabels.append(nwLabels.OUTLINE_COLS[hItem])
                self.colIndex[hItem] = i

            self.setHeaderLabels(theLabels)
            for hItem in self.treeOrder:
                self.setColumnWidth(self.colIndex[hItem], self.colWidth[hItem])
                self.setColumnHidden(self.colIndex[hItem], self.colHidden[hItem])

            # Make sure title column is always visible,
            # and handle column always hidden
            self.setColumnHidden(self.colIndex[nwOutline.TITLE], False)

            headItem = self.headerItem()
            headItem.setTextAlignment(self.colIndex[nwOutline.CCOUNT], Qt.AlignRight)
            headItem.setTextAlignment(self.colIndex[nwOutline.WCOUNT], Qt.AlignRight)
            headItem.setTextAlignment(self.colIndex[nwOutline.PCOUNT], Qt.AlignRight)

        currTitle   = None
        currChapter = None
        currScene   = None

        for tKey, tHandle, sTitle, novIdx in self.theIndex.novelStructure(skipExcluded=True):

            tItem = self._createTreeItem(tHandle, sTitle, novIdx)
            self.treeMap[tKey] = tItem

            tLevel = novIdx["level"]
            if tLevel == "H1":
                self.addTopLevelItem(tItem)
                currTitle   = tItem
                currChapter = None
                currScene   = None

            elif tLevel == "H2":
                if currTitle is None:
                    self.addTopLevelItem(tItem)
                else:
                    currTitle.addChild(tItem)
                currChapter = tItem
                currScene   = None

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

    def _createTreeItem(self, tHandle, sTitle, novIdx):
        """Populate a tree item with all the column values.
        """
        nwItem  = self.theProject.projTree[tHandle]
        newItem = QTreeWidgetItem()
        hIcon   = "doc_%s" % novIdx["level"].lower()

        cC = int(novIdx["cCount"])
        wC = int(novIdx["wCount"])
        pC = int(novIdx["pCount"])

        newItem.setText(self.colIndex[nwOutline.TITLE],  novIdx["title"])
        newItem.setData(self.colIndex[nwOutline.TITLE],  Qt.UserRole, tHandle)
        newItem.setIcon(self.colIndex[nwOutline.TITLE],  self.theTheme.getIcon(hIcon))
        newItem.setText(self.colIndex[nwOutline.LEVEL],  novIdx["level"])
        newItem.setText(self.colIndex[nwOutline.LABEL],  nwItem.itemName)
        newItem.setIcon(self.colIndex[nwOutline.LABEL],  self.theTheme.getIcon("proj_document"))
        newItem.setText(self.colIndex[nwOutline.LINE],   sTitle[1:].lstrip("0"))
        newItem.setData(self.colIndex[nwOutline.LINE],   Qt.UserRole, sTitle)
        newItem.setText(self.colIndex[nwOutline.SYNOP],  novIdx["synopsis"])
        newItem.setText(self.colIndex[nwOutline.CCOUNT], f"{cC:n}")
        newItem.setText(self.colIndex[nwOutline.WCOUNT], f"{wC:n}")
        newItem.setText(self.colIndex[nwOutline.PCOUNT], f"{pC:n}")
        newItem.setTextAlignment(self.colIndex[nwOutline.CCOUNT], Qt.AlignRight)
        newItem.setTextAlignment(self.colIndex[nwOutline.WCOUNT], Qt.AlignRight)
        newItem.setTextAlignment(self.colIndex[nwOutline.PCOUNT], Qt.AlignRight)

        theRefs = self.theIndex.getReferences(tHandle, sTitle)
        newItem.setText(self.colIndex[nwOutline.POV],    ", ".join(theRefs[nwKeyWords.POV_KEY]))
        newItem.setText(self.colIndex[nwOutline.CHAR],   ", ".join(theRefs[nwKeyWords.CHAR_KEY]))
        newItem.setText(self.colIndex[nwOutline.PLOT],   ", ".join(theRefs[nwKeyWords.PLOT_KEY]))
        newItem.setText(self.colIndex[nwOutline.TIME],   ", ".join(theRefs[nwKeyWords.TIME_KEY]))
        newItem.setText(self.colIndex[nwOutline.WORLD],  ", ".join(theRefs[nwKeyWords.WORLD_KEY]))
        newItem.setText(self.colIndex[nwOutline.OBJECT], ", ".join(theRefs[nwKeyWords.OBJECT_KEY]))
        newItem.setText(self.colIndex[nwOutline.ENTITY], ", ".join(theRefs[nwKeyWords.ENTITY_KEY]))
        newItem.setText(self.colIndex[nwOutline.CUSTOM], ", ".join(theRefs[nwKeyWords.CUSTOM_KEY]))

        return newItem

# END Class GuiOutline

class GuiOutlineHeaderMenu(QMenu):

    def __init__(self, theParent):
        QMenu.__init__(self, theParent)

        self.theParent = theParent
        self.acceptToggle = True

        mnuHead = QAction("Select Columns", self)
        self.addAction(mnuHead)
        self.addSeparator()

        self.actionMap = {}
        for hItem in nwOutline:
            if hItem == nwOutline.TITLE:
                continue
            self.actionMap[hItem] = QAction(nwLabels.OUTLINE_COLS[hItem], self)
            self.actionMap[hItem].setCheckable(True)
            self.actionMap[hItem].toggled.connect(
                lambda isChecked, tItem=hItem : self._columnToggled(isChecked, tItem)
            )
            self.addAction(self.actionMap[hItem])

        return

    def setHiddenState(self, hiddenState):
        """Overwrite the checked state of the columns as the inverse of
        the hidden state. Skip the TITLE column as it cannot be hidden.
        """
        self.acceptToggle = False

        for hItem in nwOutline:
            if hItem == nwOutline.TITLE or hItem not in hiddenState:
                continue
            self.actionMap[hItem].setChecked(not hiddenState[hItem])

        self.acceptToggle = True

        return

    ##
    #  Slots
    ##

    def _columnToggled(self, isChecked, theItem):
        """The user has toggled the visibility of a column. Forward the
        event to the parent class only if we're accepting changes.
        """
        if self.acceptToggle:
            self.theParent._menuColumnToggled(isChecked, theItem)
        return

# END Class GuiOutlineHeaderMenu

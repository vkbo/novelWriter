# -*- coding: utf-8 -*-
"""novelWriter GUI Project Outline

 novelWriter – GUI Project Outline
===================================
 Class holding the project outline view

 File History:
 Created: 2019-11-16 [0.4.1]

"""

import logging
import nw

from os import path
from time import time
from enum import Enum

from PyQt5.QtCore import Qt, QByteArray
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QMenu, QAction,
    QAbstractItemView
)

from nw.constants import nwKeyWords, nwLabels

logger = logging.getLogger(__name__)

class HCols(Enum):

    TITLE  = 0
    LEVEL  = 1
    LABEL  = 2
    LINE   = 3
    WCOUNT = 4
    CCOUNT = 5
    PCOUNT = 6
    SYNOP  = 7
    POV    = 8
    CHAR   = 9
    PLOT   = 10
    TIME   = 11
    WORLD  = 12
    OBJECT = 13
    ENTITY = 14
    CUSTOM = 15

# END Enum HCols

class GuiProjectOutline(QTreeWidget):

    COL_LABELS = {
        HCols.TITLE  : "Title",
        HCols.LEVEL  : "Level",
        HCols.LABEL  : "Document",
        HCols.LINE   : "Line",
        HCols.WCOUNT : "Words",
        HCols.CCOUNT : "Chars",
        HCols.PCOUNT : "Pars",
        HCols.POV    : "POV",
        HCols.CHAR   : nwLabels.KEY_NAME[nwKeyWords.CHAR_KEY],
        HCols.PLOT   : nwLabels.KEY_NAME[nwKeyWords.PLOT_KEY],
        HCols.TIME   : nwLabels.KEY_NAME[nwKeyWords.TIME_KEY],
        HCols.WORLD  : nwLabels.KEY_NAME[nwKeyWords.WORLD_KEY],
        HCols.OBJECT : nwLabels.KEY_NAME[nwKeyWords.OBJECT_KEY],
        HCols.ENTITY : nwLabels.KEY_NAME[nwKeyWords.ENTITY_KEY],
        HCols.CUSTOM : nwLabels.KEY_NAME[nwKeyWords.CUSTOM_KEY],
        HCols.SYNOP  : "Synopsis",
    }

    def __init__(self, theParent, theProject):
        QTreeWidget.__init__(self, theParent)

        logger.debug("Initialising ProjectOutline ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
        self.theIndex   = self.theParent.theIndex
        self.optState   = self.theProject.optState
        self.headerMenu = GuiOutlineHeaderMenu(self)

        self.firstView = True
        self.lastBuild = 0

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setExpandsOnDoubleClick(False)
        self.setDragEnabled(False)
        self.itemDoubleClicked.connect(self._treeDoubleClick)

        self.treeHead = self.header()
        self.treeHead.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeHead.customContextMenuRequested.connect(self._headerRightClick)
        self.treeHead.sectionMoved.connect(self._columnMoved)

        self.treeMap   = {}
        self.treeOrder = self.COL_LABELS.keys()
        self.treeNCols = len(self.treeOrder)
        self.treeWidth = [150]*self.treeNCols
        self.colIndex  = {}

        logger.debug("ProjectOutline initialisation complete")

        return

    def refreshTree(self):
        """Called whenever the Outline tab is activated and controls
        what data to load, and if necessary, force a rebuild of the
        tree.
        """

        if self.firstView:
            self._loadHeaderState()
            self._populateTree()

        self.firstView = False

        return

    def closeOutline(self):
        """Called before a project is closed.
        """
        self._saveHeaderState()
        self.clear()
        self.firstView = True
        return

    ##
    #  Slots
    ##

    def _treeDoubleClick(self, tItem, tCol):
        print(tItem, tCol)
        return

    def _headerRightClick(self, clickPos):
        print(clickPos)
        globPos = self.mapToGlobal(clickPos)
        print(globPos)
        return

    def _columnMoved(self, logIdx, oldVisualIdx, newVisualIdx):
        """Make sure the order and width read from settings file, or
        with default values, is kept up-to-date when columns are moved
        around. Otherwise, the original order will be restored on a tree
        rebuild.
        """
        self.treeOrder.insert(newVisualIdx, self.treeOrder.pop(oldVisualIdx))
        self.treeWidth.insert(newVisualIdx, self.treeWidth.pop(oldVisualIdx))
        return

    ##
    #  Internal Functions
    ##

    def _loadHeaderState(self):
        """Load the state of the main tree header, that is, column order
        and column width.
        """

        # Load whatever we saved last time, regardless of wether it
        # contains the correct names or number of columns.
        keysOrder = self.COL_LABELS.keys()
        tempOrder = self.optState.getValue("GuiProjectOutline", "headerOrder", keysOrder)
        treeOrder = []
        for hName in tempOrder:
            for hItem in HCols:
                if hItem.name == hName:
                    treeOrder.append(hItem)

        # Add columns that were not in tempOrder to treeOrder, but in
        # the default column order.
        for cItem in keysOrder:
            if cItem not in treeOrder:
                treeOrder.append(cItem)

        # Check that we now have a complete list, and only if so, save
        # the order loaded from file. Otherwise, we keep the default.
        if len(treeOrder) == self.treeNCols:
            self.treeOrder = treeOrder
        else:
            logger.error("Failed to extract outline column order from previous session")
            logger.error("Column count doesn't match %d != %d" % (len(treeOrder), self.treeNCols))

        # The columns widths we just fill whatever we've got, and append
        # the rest with defaults, and truncate to desired length.
        tempWidth = self.optState.getValue("GuiProjectOutline", "headerWidth", [])
        treeWidth = [int(w) for w in tempWidth]
        self.treeWidth = (treeWidth + self.treeWidth)[0:self.treeNCols]

        return

    def _saveHeaderState(self):
        """Save the state of the main tree header, that is, column order
        and column width.
        """

        treeWidth = []
        treeOrder = []
        for iCol in range(self.columnCount()):
            treeOrder.append(self.treeOrder[iCol].name)
            iLog = self.treeHead.logicalIndex(iCol)
            treeWidth.append(self.columnWidth(iLog))

        self.optState.setValue("GuiProjectOutline", "headerOrder", treeOrder)
        self.optState.setValue("GuiProjectOutline", "headerWidth", treeWidth)
        self.optState.saveSettings()

        return

    def _populateTree(self):
        """Build the tree based on the project index.
        """

        theLabels = []
        for i, hItem in enumerate(self.treeOrder):
            theLabels.append(self.COL_LABELS[hItem])
            self.colIndex[hItem] = i

        self.clear()
        self.setHeaderLabels(theLabels)
        for n, colW in enumerate(self.treeWidth):
            self.setColumnWidth(n,colW)

        headItem = self.headerItem()
        headItem.setTextAlignment(self.colIndex[HCols.CCOUNT],Qt.AlignRight)
        headItem.setTextAlignment(self.colIndex[HCols.WCOUNT],Qt.AlignRight)
        headItem.setTextAlignment(self.colIndex[HCols.PCOUNT],Qt.AlignRight)

        currTitle   = None
        currChapter = None
        currScene   = None

        for titleKey in self.theIndex.getNovelStructure():

            if len(titleKey) < 16:
                continue

            tHandle = titleKey[:13]
            sTitle  = titleKey[14:]

            if tHandle not in self.theIndex.novelIndex:
                continue
            if sTitle not in self.theIndex.novelIndex[tHandle]:
                continue

            tLevel = self.theIndex.novelIndex[tHandle][sTitle]["level"]
            tTime  = self.theIndex.novelIndex[tHandle][sTitle]["updated"]
            tItem  = self._createTreeItem(tHandle, sTitle)
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

    def _createTreeItem(self, tHandle, sTitle):
        """Populate a tree item with all the column values.
        """

        nwItem = self.theProject.getItem(tHandle)
        novIdx = self.theIndex.novelIndex[tHandle][sTitle]

        newItem = QTreeWidgetItem()

        newItem.setText(self.colIndex[HCols.TITLE],  novIdx["title"])
        newItem.setText(self.colIndex[HCols.LEVEL],  novIdx["level"])
        newItem.setText(self.colIndex[HCols.LABEL],  nwItem.itemName)
        newItem.setText(self.colIndex[HCols.LINE],   sTitle[1:])
        newItem.setText(self.colIndex[HCols.SYNOP],  novIdx["synopsis"])
        newItem.setText(self.colIndex[HCols.CCOUNT], str(novIdx["cCount"]))
        newItem.setText(self.colIndex[HCols.WCOUNT], str(novIdx["wCount"]))
        newItem.setText(self.colIndex[HCols.PCOUNT], str(novIdx["pCount"]))
        newItem.setTextAlignment(self.colIndex[HCols.CCOUNT], Qt.AlignRight)
        newItem.setTextAlignment(self.colIndex[HCols.WCOUNT], Qt.AlignRight)
        newItem.setTextAlignment(self.colIndex[HCols.PCOUNT], Qt.AlignRight)

        theRefs = self.theIndex.getReferences(tHandle, sTitle)
        newItem.setText(self.colIndex[HCols.POV],    ", ".join(theRefs[nwKeyWords.POV_KEY]))
        newItem.setText(self.colIndex[HCols.CHAR],   ", ".join(theRefs[nwKeyWords.CHAR_KEY]))
        newItem.setText(self.colIndex[HCols.PLOT],   ", ".join(theRefs[nwKeyWords.PLOT_KEY]))
        newItem.setText(self.colIndex[HCols.TIME],   ", ".join(theRefs[nwKeyWords.TIME_KEY]))
        newItem.setText(self.colIndex[HCols.WORLD],  ", ".join(theRefs[nwKeyWords.WORLD_KEY]))
        newItem.setText(self.colIndex[HCols.OBJECT], ", ".join(theRefs[nwKeyWords.OBJECT_KEY]))
        newItem.setText(self.colIndex[HCols.ENTITY], ", ".join(theRefs[nwKeyWords.ENTITY_KEY]))
        newItem.setText(self.colIndex[HCols.CUSTOM], ", ".join(theRefs[nwKeyWords.CUSTOM_KEY]))

        return newItem

# END Class GuiProjectOutline

class GuiOutlineHeaderMenu(QMenu):

    def __init__(self, theParent):
        QMenu.__init__(self, theParent)

        return

# END Class GuiOutlineHeaderMenu

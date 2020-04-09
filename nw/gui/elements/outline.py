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

from nw.constants import nwKeyWords, nwLabels, nwOutline

logger = logging.getLogger(__name__)

class GuiProjectOutline(QTreeWidget):

    COL_DEF = {
        nwOutline.TITLE  : (200, True,  nwLabels.OUTLINE_COLS[nwOutline.TITLE]),
        nwOutline.LEVEL  : ( 40, False, nwLabels.OUTLINE_COLS[nwOutline.LEVEL]),
        nwOutline.LABEL  : (150, True,  nwLabels.OUTLINE_COLS[nwOutline.LABEL]),
        nwOutline.LINE   : ( 40, False, nwLabels.OUTLINE_COLS[nwOutline.LINE]),
        nwOutline.CCOUNT : ( 50, False, nwLabels.OUTLINE_COLS[nwOutline.CCOUNT]),
        nwOutline.WCOUNT : ( 50, True,  nwLabels.OUTLINE_COLS[nwOutline.WCOUNT]),
        nwOutline.PCOUNT : ( 50, True,  nwLabels.OUTLINE_COLS[nwOutline.PCOUNT]),
        nwOutline.POV    : (100, True,  nwLabels.OUTLINE_COLS[nwOutline.POV]),
        nwOutline.CHAR   : (100, True,  nwLabels.OUTLINE_COLS[nwOutline.CHAR]),
        nwOutline.PLOT   : (100, True,  nwLabels.OUTLINE_COLS[nwOutline.PLOT]),
        nwOutline.TIME   : (100, False, nwLabels.OUTLINE_COLS[nwOutline.TIME]),
        nwOutline.WORLD  : (100, True,  nwLabels.OUTLINE_COLS[nwOutline.WORLD]),
        nwOutline.OBJECT : (100, False, nwLabels.OUTLINE_COLS[nwOutline.OBJECT]),
        nwOutline.ENTITY : (100, False, nwLabels.OUTLINE_COLS[nwOutline.ENTITY]),
        nwOutline.CUSTOM : (100, False, nwLabels.OUTLINE_COLS[nwOutline.CUSTOM]),
        nwOutline.SYNOP  : (200, True,  nwLabels.OUTLINE_COLS[nwOutline.SYNOP]),
    }

    def __init__(self, theParent, theProject):
        QTreeWidget.__init__(self, theParent)

        logger.debug("Initialising ProjectOutline ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
        self.theIndex   = self.theParent.theIndex
        self.optState   = self.theProject.optState
        self.headerMenu = GuiOutlineHeaderMenu(self, self.COL_DEF, nwOutline.TITLE)

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
        self.treeOrder = self.COL_DEF.keys()
        self.treeNCols = len(self.treeOrder)
        self.colWidth  = [150]*self.treeNCols
        self.colHidden = [False]*self.treeNCols
        self.colIndex  = {}

        # Set defaults
        for hItem in self.treeOrder:
            self.colWidth[hItem.value] = self.COL_DEF[hItem][0]
            self.colHidden[hItem.value] = self.COL_DEF[hItem][1]

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
        self.headerMenu.exec_(self.mapToGlobal(clickPos))
        print("Menu closed")
        return

    def _columnMoved(self, logIdx, oldVisualIdx, newVisualIdx):
        """Make sure the order and width read from settings file, or
        with default values, is kept up-to-date when columns are moved
        around. Otherwise, the original order will be restored on a tree
        rebuild.
        """
        self.treeOrder.insert(newVisualIdx, self.treeOrder.pop(oldVisualIdx))
        self.colWidth.insert(newVisualIdx, self.colWidth.pop(oldVisualIdx))
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
        keysOrder = self.COL_DEF.keys()
        tempOrder = self.optState.getValue("GuiProjectOutline", "headerOrder", keysOrder)
        treeOrder = []
        for hName in tempOrder:
            for hItem in nwOutline:
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

        # The columns widths and hidden state we just fill with whatever
        # we've got, and append the rest with defaults, and truncate to
        # desired length.
        tmpWidth = self.optState.getValue("GuiProjectOutline", "columnWidth", [])
        colWidth = [int(w) for w in tmpWidth]
        self.colWidth = (colWidth + self.colWidth)[0:self.treeNCols]

        tmpHidden = self.optState.getValue("GuiProjectOutline", "columnHidden", [])
        colHidden = [int(w) for w in tmpHidden]
        self.colHidden = (colHidden + self.colHidden)[0:self.treeNCols]

        return

    def _saveHeaderState(self):
        """Save the state of the main tree header, that is, column order
        and column width.
        """

        # If we haven't built the tree, there is nothing to save.
        if self.lastBuild == 0:
            return

        treeOrder = []
        colWidth  = []
        colHidden = []
        for iCol in range(self.columnCount()):
            treeOrder.append(self.treeOrder[iCol].name)
            iLog = self.treeHead.logicalIndex(iCol)
            colWidth.append(self.columnWidth(iLog))
            colHidden.append(self.isColumnHidden(iLog))

        self.optState.setValue("GuiProjectOutline", "headerOrder",  treeOrder)
        self.optState.setValue("GuiProjectOutline", "columnWidth",  colWidth)
        self.optState.setValue("GuiProjectOutline", "columnHidden", colHidden)
        self.optState.saveSettings()

        return

    def _populateTree(self):
        """Build the tree based on the project index.
        """

        theLabels = []
        for i, hItem in enumerate(self.treeOrder):
            theLabels.append(self.COL_DEF[hItem][2])
            self.colIndex[hItem] = i

        self.clear()
        self.setHeaderLabels(theLabels)
        for n, colW in enumerate(self.colWidth):
            self.setColumnWidth(n,colW)

        headItem = self.headerItem()
        headItem.setTextAlignment(self.colIndex[nwOutline.CCOUNT], Qt.AlignRight)
        headItem.setTextAlignment(self.colIndex[nwOutline.WCOUNT], Qt.AlignRight)
        headItem.setTextAlignment(self.colIndex[nwOutline.PCOUNT], Qt.AlignRight)

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

        newItem.setText(self.colIndex[nwOutline.TITLE],  novIdx["title"])
        newItem.setText(self.colIndex[nwOutline.LEVEL],  novIdx["level"])
        newItem.setText(self.colIndex[nwOutline.LABEL],  nwItem.itemName)
        newItem.setText(self.colIndex[nwOutline.LINE],   sTitle[1:])
        newItem.setText(self.colIndex[nwOutline.SYNOP],  novIdx["synopsis"])
        newItem.setText(self.colIndex[nwOutline.CCOUNT], str(novIdx["cCount"]))
        newItem.setText(self.colIndex[nwOutline.WCOUNT], str(novIdx["wCount"]))
        newItem.setText(self.colIndex[nwOutline.PCOUNT], str(novIdx["pCount"]))
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

# END Class GuiProjectOutline

class GuiOutlineHeaderMenu(QMenu):

    def __init__(self, theParent, colDefault, skipCol):
        QMenu.__init__(self, theParent)

        mnuHead = QAction("Select Columns", self)
        self.addAction(mnuHead)
        self.addSeparator()

        self.actionMap = {}

        for hItem in nwOutline:
            if hItem == skipCol:
                continue
            if hItem not in colDefault:
                continue
            self.actionMap[hItem] = QAction(colDefault[hItem][2], self)
            self.actionMap[hItem].setCheckable(True)
            self.actionMap[hItem].setChecked(colDefault[hItem][1])
            self.actionMap[hItem].toggled.connect(
                lambda isChecked, tItem=hItem : self._columnToggled(isChecked, tItem)
            )
            self.addAction(self.actionMap[hItem])

        return

    def _columnToggled(self, isChecked, theItem):
        print(isChecked, theItem.name)
        return

# END Class GuiOutlineHeaderMenu

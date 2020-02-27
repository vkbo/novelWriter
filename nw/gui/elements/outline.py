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

from PyQt5.QtCore import Qt, QByteArray
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem
)

from nw.constants import nwKeyWords, nwLabels

logger = logging.getLogger(__name__)

class GuiProjectOutline(QWidget):

    I_TITLE  = 0
    I_LEVEL  = 1
    I_LABEL  = 2
    I_LINE   = 3
    I_WCOUNT = 4
    I_CCOUNT = 5
    I_PCOUNT = 6
    I_SYNOP  = 7
    I_POV    = 8
    I_CHAR   = 9
    I_PLOT   = 10
    I_TIME   = 11
    I_WORLD  = 12
    I_OBJECT = 13
    I_ENTITY = 14
    I_CUSTOM = 15

    COL_MAX = 15

    COL_LABELS = {
        I_TITLE  : "Title",
        I_LEVEL  : "Level",
        I_LABEL  : "Document",
        I_LINE   : "Line",
        I_WCOUNT : "Words",
        I_CCOUNT : "Chars",
        I_PCOUNT : "Pars",
        I_SYNOP  : "Synopsis",
        I_POV    : "POV",
        I_CHAR   : nwLabels.KEY_NAME[nwKeyWords.CHAR_KEY],
        I_PLOT   : nwLabels.KEY_NAME[nwKeyWords.PLOT_KEY],
        I_TIME   : nwLabels.KEY_NAME[nwKeyWords.TIME_KEY],
        I_WORLD  : nwLabels.KEY_NAME[nwKeyWords.WORLD_KEY],
        I_OBJECT : nwLabels.KEY_NAME[nwKeyWords.OBJECT_KEY],
        I_ENTITY : nwLabels.KEY_NAME[nwKeyWords.ENTITY_KEY],
        I_CUSTOM : nwLabels.KEY_NAME[nwKeyWords.CUSTOM_KEY],
    }

    def __init__(self, theParent, theProject):
        QWidget.__init__(self, theParent)

        logger.debug("Initialising ProjectOutline ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
        self.theIndex   = self.theParent.theIndex
        self.optState   = self.theProject.optState

        self.firstView = True

        self.outerBox  = QVBoxLayout()
        self.mainTree  = QTreeWidget()
        self.lastBuild = 0
        self.treeMap   = {}
        self.treeCols  = {
            "order" : [
                self.I_TITLE,  self.I_LABEL,
                self.I_WCOUNT, self.I_POV,
                self.I_CHAR,   self.I_PLOT,
                self.I_WORLD,  self.I_SYNOP
            ],
            "width" : [150, 100, 80, 100, 100, 100, 100, 300],
        }
        self.colIndex = {}

        self.outerBox.addWidget(self.mainTree)
        self.outerBox.setContentsMargins(0,0,0,0)
        self.setLayout(self.outerBox)

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
        self.mainTree.clear()
        self.firstView = True

        return

    ##
    #  Internal Functions
    ##

    def _loadHeaderState(self):
        """Load the state of the main tree header, that is, column order
        and column width.
        """

        treeCols = self.optState.getValue("GuiProjectOutline", "headerState", self.treeCols)

        if "order" not in treeCols.keys(): return
        if not isinstance(treeCols["order"], list): return
        if len(treeCols["order"]) == 0: return

        self.treeCols["order"] = []
        for colID in treeCols["order"]:
            if colID >= 0 and colID <= self.COL_MAX:
                self.treeCols["order"].append(colID)

        if "width" in treeCols.keys():
            if isinstance(treeCols["width"],list):
                self.treeCols["width"] = treeCols["width"]

        return

    def _saveHeaderState(self):
        """Save the state of the main tree header, that is, column order
        and column width.
        """

        colW = []
        for iCol in range(self.mainTree.columnCount()):
            colW.append(self.mainTree.columnWidth(iCol))

        self.treeCols["width"] = colW
        self.optState.setValue("GuiProjectOutline", "headerState", self.treeCols)
        self.optState.saveSettings()

        return

    def _populateTree(self):
        """Build the tree based on the project index.
        """

        theLabels = []
        for i, n in enumerate(self.treeCols["order"]):
            theLabels.append(self.COL_LABELS[n])
            self.colIndex[n] = i

        self.mainTree.clear()
        self.mainTree.setHeaderLabels(theLabels)
        for n, colW in enumerate(self.treeCols["width"]):
            self.mainTree.setColumnWidth(n,colW)

        treeHead = self.mainTree.headerItem()
        if self.I_CCOUNT in self.colIndex:
            treeHead.setTextAlignment(self.colIndex[self.I_CCOUNT],Qt.AlignRight)
        if self.I_WCOUNT in self.colIndex:
            treeHead.setTextAlignment(self.colIndex[self.I_WCOUNT],Qt.AlignRight)
        if self.I_PCOUNT in self.colIndex:
            treeHead.setTextAlignment(self.colIndex[self.I_PCOUNT],Qt.AlignRight)

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
                self.mainTree.addTopLevelItem(tItem)
            elif tLevel == "H2":
                if currTitle is None:
                    self.mainTree.addTopLevelItem(tItem)
                else:
                    currTitle.addChild(tItem)
                currChapter = tItem
            elif tLevel == "H3":
                if currChapter is None:
                    if currTitle is None:
                        self.mainTree.addTopLevelItem(tItem)
                    else:
                        currTitle.addChild(tItem)
                else:
                    currChapter.addChild(tItem)
                currScene = tItem
            elif tLevel == "H4":
                if currScene is None:
                    if currChapter is None:
                        if currTitle is None:
                            self.mainTree.addTopLevelItem(tItem)
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
        self._setItemText(newItem, self.I_TITLE,  novIdx["title"])
        self._setItemText(newItem, self.I_LEVEL,  novIdx["level"])
        self._setItemText(newItem, self.I_LABEL,  nwItem.itemName)
        self._setItemText(newItem, self.I_LINE,   sTitle[1:])
        self._setItemText(newItem, self.I_SYNOP,  novIdx["synopsis"])
        self._setItemText(newItem, self.I_CCOUNT, str(novIdx["cCount"]), True)
        self._setItemText(newItem, self.I_WCOUNT, str(novIdx["wCount"]), True)
        self._setItemText(newItem, self.I_PCOUNT, str(novIdx["pCount"]), True)

        theRefs = self.theIndex.getReferences(tHandle, sTitle)
        self._setItemText(newItem, self.I_POV,    ", ".join(theRefs[nwKeyWords.POV_KEY]))
        self._setItemText(newItem, self.I_CHAR,   ", ".join(theRefs[nwKeyWords.CHAR_KEY]))
        self._setItemText(newItem, self.I_PLOT,   ", ".join(theRefs[nwKeyWords.PLOT_KEY]))
        self._setItemText(newItem, self.I_TIME,   ", ".join(theRefs[nwKeyWords.TIME_KEY]))
        self._setItemText(newItem, self.I_WORLD,  ", ".join(theRefs[nwKeyWords.WORLD_KEY]))
        self._setItemText(newItem, self.I_OBJECT, ", ".join(theRefs[nwKeyWords.OBJECT_KEY]))
        self._setItemText(newItem, self.I_ENTITY, ", ".join(theRefs[nwKeyWords.ENTITY_KEY]))
        self._setItemText(newItem, self.I_CUSTOM, ", ".join(theRefs[nwKeyWords.CUSTOM_KEY]))

        return newItem

    def _setItemText(self, tItem, colID, theText, rAlign=False):
        """Set the correct text in the correct column, and if necessary,
        right align it.
        """
        if colID in self.colIndex:
            tItem.setText(self.colIndex[colID], theText)
            if rAlign:
                tItem.setTextAlignment(self.colIndex[colID], Qt.AlignRight)
        return

# END Class GuiProjectOutline

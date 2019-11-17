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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem
)

from nw.constants import nwItemLayout, nwKeyWords, nwLabels

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

    COL_ORDER = [
        I_TITLE,  I_LEVEL,  I_LABEL,  I_LINE,
        I_WCOUNT, I_CCOUNT, I_PCOUNT, I_SYNOP,
        I_POV,    I_CHAR,   I_PLOT,   I_TIME,
        I_WORLD,  I_OBJECT, I_ENTITY, I_CUSTOM,
    ]

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

        self.showWords    = True
        self.showSynopsis = True
        self.showFilePath = False

        self.outerBox  = QVBoxLayout()
        self.mainTree  = QTreeWidget()
        self.treeCols  = self.COL_ORDER
        self.lastBuild = 0
        self.treeMap   = {}

        self.outerBox.addWidget(self.mainTree)
        self.outerBox.setContentsMargins(0,0,0,0)
        self.setLayout(self.outerBox)

        logger.debug("ProjectOutline initialisation complete")

        return

    def populateTree(self):

        theLabels = []
        for n in self.treeCols:
            theLabels.append(self.COL_LABELS[n])

        self.mainTree.clear()
        self.mainTree.setHeaderLabels(theLabels)

        treeHead = self.mainTree.headerItem()
        treeHead.setTextAlignment(self.I_CCOUNT,Qt.AlignRight)
        treeHead.setTextAlignment(self.I_WCOUNT,Qt.AlignRight)
        treeHead.setTextAlignment(self.I_PCOUNT,Qt.AlignRight)

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

    ##
    #  Internal Functions
    ##

    def _createTreeItem(self, tHandle, sTitle):

        nwItem = self.theProject.getItem(tHandle)
        novIdx = self.theIndex.novelIndex[tHandle][sTitle]

        newItem = QTreeWidgetItem()
        newItem.setText(self.I_TITLE, novIdx["title"])
        newItem.setText(self.I_LEVEL, novIdx["level"])
        newItem.setText(self.I_LABEL, nwItem.itemName)
        newItem.setText(self.I_LINE,  sTitle[1:])

        newItem.setText(self.I_CCOUNT, str(novIdx["cCount"]))
        newItem.setText(self.I_WCOUNT, str(novIdx["wCount"]))
        newItem.setText(self.I_PCOUNT, str(novIdx["pCount"]))
        newItem.setTextAlignment(self.I_CCOUNT,Qt.AlignRight)
        newItem.setTextAlignment(self.I_WCOUNT,Qt.AlignRight)
        newItem.setTextAlignment(self.I_PCOUNT,Qt.AlignRight)

        theRefs = self.theIndex.getReferences(tHandle, sTitle)
        newItem.setText(self.I_POV,    ", ".join(theRefs[nwKeyWords.POV_KEY]))
        newItem.setText(self.I_CHAR,   ", ".join(theRefs[nwKeyWords.CHAR_KEY]))
        newItem.setText(self.I_PLOT,   ", ".join(theRefs[nwKeyWords.PLOT_KEY]))
        newItem.setText(self.I_TIME,   ", ".join(theRefs[nwKeyWords.TIME_KEY]))
        newItem.setText(self.I_WORLD,  ", ".join(theRefs[nwKeyWords.WORLD_KEY]))
        newItem.setText(self.I_OBJECT, ", ".join(theRefs[nwKeyWords.OBJECT_KEY]))
        newItem.setText(self.I_ENTITY, ", ".join(theRefs[nwKeyWords.ENTITY_KEY]))
        newItem.setText(self.I_CUSTOM, ", ".join(theRefs[nwKeyWords.CUSTOM_KEY]))

        return newItem

# END Class GuiProjectOutline
